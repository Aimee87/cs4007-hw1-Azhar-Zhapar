# registration_bot.py
# -*- coding: utf-8 -*-
"""
Registrar comparison script (OpenRouter / OpenAI fallback patterns).
Save as registration_bot.py and run from project root.
"""
import os
import time
import json
import traceback
from pathlib import Path
from typing import List, Dict, Any

import requests

# Configuration
OPENROUTER_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_DEFAULT_MODEL = "deepseek/deepseek-v4-flash-0731"
OPENAI_DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
CATALOGUE = Path(__file__).resolve().parent.parent / "data" / "courses.json"

RATES_PER_MTOK = {
    "deepseek/deepseek-v4-flash-0731": (0.14, 0.28),
    "gpt-4o-mini": (0.06, 0.12),
}

# Utilities
def load_catalogue() -> dict:
    if not CATALOGUE.exists():
        return {"credit_limit": 18, "student": {"completed": []}, "rules": {"max_credits": 18}, "courses": []}
    return json.loads(CATALOGUE.read_text(encoding="utf-8"))

def short(text: str, n: int = 300) -> str:
    if text is None:
        return ""
    return (text[:n] + "...") if len(text) > n else text

def safe_json(obj):
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except Exception:
        return str(obj)

# System prompt builder
def build_system_prompt(catalogue: dict) -> str:
    lines = []
    lines.append("You are the Narxoz course registrar. Answer concisely and refuse anything not in the catalogue.")
    credit_limit = catalogue.get("credit_limit", 18)
    lines.append(f"Student credit limit: {credit_limit}")
    student = catalogue.get("student", {})
    completed = student.get("completed", [])
    lines.append("Student completed courses: " + (", ".join(completed) if completed else "none"))
    rules = catalogue.get("rules", {})
    lines.append(f"Rules: max_credits={rules.get('max_credits','?')}, min_credits={rules.get('min_credits','?')}")
    lines.append("Catalogue courses:")
    for c in catalogue.get("courses", []):
        code = c.get("code", "")
        title = c.get("title", "")
        credits = c.get("credits", "")
        prereq = ", ".join(c.get("prerequisites", [])) or "none"
        seats_total = c.get("seats_total", 0)
        seats_taken = c.get("seats_taken", 0)
        schedule = "; ".join([f'{s.get("day")} {s.get("start")}-{s.get("end")}' for s in c.get("schedule", [])])
        lines.append(f"- {code}: {title}; credits={credits}; prereq={prereq}; schedule={schedule}; seats {seats_taken}/{seats_total}")
    lines.append("If asked about any course not listed above, refuse and do not invent details.")
    return "\n".join(lines)

# Robust usage extraction
def _extract_usage(resp) -> tuple[int, int]:
    try:
        usage_obj = getattr(resp, "usage", None)
        if usage_obj is not None:
            input_tokens = getattr(usage_obj, "prompt_tokens", None)
            output_tokens = getattr(usage_obj, "completion_tokens", None)
            if input_tokens is not None or output_tokens is not None:
                return int(input_tokens or 0), int(output_tokens or 0)
            if hasattr(usage_obj, "get"):
                input_tokens = usage_obj.get("prompt_tokens", usage_obj.get("input_tokens"))
                output_tokens = usage_obj.get("completion_tokens", usage_obj.get("output_tokens"))
                if input_tokens is not None or output_tokens is not None:
                    return int(input_tokens or 0), int(output_tokens or 0)
    except Exception:
        pass

    try:
        if isinstance(resp, dict):
            usage = resp.get("usage", {})
            input_tokens = usage.get("prompt_tokens", usage.get("input_tokens", 0))
            output_tokens = usage.get("completion_tokens", usage.get("output_tokens", 0))
            return int(input_tokens or 0), int(output_tokens or 0)
    except Exception:
        pass

    try:
        usage_any = getattr(resp, "usage", None) or (resp.get("usage") if isinstance(resp, dict) else None)
        if usage_any:
            total = getattr(usage_any, "total_tokens", None) or (usage_any.get("total_tokens") if isinstance(usage_any, dict) else None)
            if total:
                t = int(total)
                return t // 2, t - (t // 2)
    except Exception:
        pass

    return 0, 0

# Client selection for OpenRouter (we use REST for OpenAI in other parts)
def client_for(via: str):
    if via == "openrouter":
        # We will use REST requests for OpenRouter in this script
        return None
    raise ValueError('via must be "openrouter"')

# Chat wrapper for OpenRouter client objects (if using SDK) or REST
def chat(messages, model=OPENROUTER_DEFAULT_MODEL, via="openrouter"):
    # Prefer REST call for OpenRouter to avoid SDK mismatch
    if via == "openrouter":
        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise RuntimeError("OPENROUTER_API_KEY not set")
        url = OPENROUTER_BASE_URL.rstrip("/") + "/chat/completions"
        payload = {"model": model, "messages": messages}
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        resp_obj = None
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            r.raise_for_status()
            resp_obj = r.json()
        except Exception as e:
            raise
        # extract text
        try:
            text = resp_obj["choices"][0]["message"]["content"]
        except Exception:
            text = safe_json(resp_obj)
        input_tokens, output_tokens = _extract_usage(resp_obj)
        if input_tokens == 0 and output_tokens == 0:
            print("DEBUG: couldn't extract tokens cleanly. Dumping resp for inspection:")
            try:
                import pprint
                pprint.pprint(resp_obj)
            except Exception:
                print(resp_obj)
        return {"text": text, "input_tokens": input_tokens, "output_tokens": output_tokens, "model": model}

    # fallback: not supported
    raise ValueError("Unsupported via value for chat()")

# Conversation helpers
def new_conversation(catalogue: dict) -> list[dict]:
    return [{"role": "system", "content": build_system_prompt(catalogue)}]

def run_turn(history: list[dict], user_text: str, model=OPENROUTER_DEFAULT_MODEL, via="openrouter"):
    history = history + [{"role": "user", "content": user_text}]
    reply = chat(history, model=model, via=via)
    history = history + [{"role": "assistant", "content": reply["text"]}]
    return history, reply

# Cost estimation
def estimate_cost(input_tokens: int, output_tokens: int, rate_in: float, rate_out: float) -> float:
    cost_in = (input_tokens / 1_000_000) * rate_in
    cost_out = (output_tokens / 1_000_000) * rate_out
    return cost_in + cost_out

def cost_of(usage: dict) -> float:
    rate_in, rate_out = RATES_PER_MTOK.get(usage.get("model"), (0.0, 0.0))
    return estimate_cost(usage.get("input_tokens", 0), usage.get("output_tokens", 0), rate_in, rate_out)

def conversation_cost(usages: list[dict]) -> float:
    return sum(cost_of(u) for u in usages)

# Script to run
SCRIPT = [
    "I am a third-year student. Which courses am I still eligible to register for?",
    "Register me for CSS-4007 and CSS-4102.",
    "How many credits would that be in total, and am I within the limit?",
    "Add CSS-4090 Quantum Machine Learning to my schedule.",
    "Я учусь на третьем курсе. На какие предметы я еще могу записаться?",
]

def run_script(model=OPENROUTER_DEFAULT_MODEL, via="openrouter"):
    history = new_conversation(load_catalogue())
    usages = []
    print("\n===== " + via + " / " + model + " =====")
    for i, user_text in enumerate(SCRIPT, start=1):
        history, usage = run_turn(history, user_text, model=model, via=via)
        usages.append(usage)
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        rate_in, rate_out = RATES_PER_MTOK.get(model, (0.0, 0.0))
        cost = estimate_cost(input_tokens, output_tokens, rate_in, rate_out)
        print("\n--- turn %d ---" % i)
        print("you: " + user_text)
        print("bot: " + usage.get("text", ""))
        print(f"     in={input_tokens:6d}  out={output_tokens:5d}  ${cost:.6f}")
    print("\n%10s%8s%7s%12s" % ("", "in", "out", "cost"))
    for i, u in enumerate(usages, start=1):
        print("turn %-5d%8d%7d%12.6f" % (i, u["input_tokens"], u["output_tokens"], cost_of(u)))
    print("%25s%s" % ("", "-" * 12))
    print("%25s%12.6f" % ("total", conversation_cost(usages)))
    return usages

if __name__ == "__main__":
    try:
        run_script()
    except Exception:
        traceback.print_exc()
