# -*- coding: utf-8 -*-
import json, os, requests, time
from pathlib import Path
from openai import OpenAI

MODELS = [
    ("openrouter","google/gemma-4-26b-a4b-it:free"),
    ("openrouter","qwen/qwen3.8-27b"),
    ("openrouter","deepseek/deepseek-v4-flash-0731"),
    ("openai","gpt-5.6-luna"),
    ("openai","gpt-5.6-terra"),
    ("openai","gpt-5.6-sol"),
]

DATA = Path(__file__).resolve().parent.parent/"data"/"kazakh_errors.json"

def load_sentences(limit=2):
    return json.loads(DATA.read_text(encoding="utf-8"))["sentences"][:limit]

def build_prompt(corrupted):
    return ('Correct the Kazakh sentence and list changes. '
            'Return ONLY JSON: {"corrected":"...","changes":["..."]}\n\n'
            f'Input: "{corrupted}"')

def ask_once(model, via, prompt):
    try:
        if via == "openrouter":
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                       "Content-Type": "application/json"}
            payload = {"model": model, "messages":[{"role":"user","content":prompt}]}
            r = requests.post(url, headers=headers, json=payload, timeout=15)
            r.raise_for_status()
            d = r.json()
            return d["choices"][0]["message"]["content"]
        elif via == "openai":
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            r = client.chat.completions.create(model=model,
                                               messages=[{"role":"user","content":prompt}],
                                               timeout=15)
            return r.choices[0].message.content
    except Exception as e:
        return f'{{"corrected":"","changes":[],"error":"{e}"}}'

def parse_response(text):
    try:
        s, e = text.find("{"), text.rfind("}")+1
        return json.loads(text[s:e])
    except:
        return {"corrected":"", "changes":[]}

def run_all():
    rows=[]
    for via,model in MODELS:
        for s in load_sentences():
            reply = ask_once(model, via, build_prompt(s["corrupted"]))
            parsed = parse_response(reply)
            rows.append({
                "model":model,
                "id":s["id"],
                "correct":s["correct"],
                "corrupted":s["corrupted"],
                "changes":parsed.get("changes",[]),
                "corrected":parsed.get("corrected",""),
                "exact": (parsed.get("corrected","")==s["correct"]),
                "failed": "error" in parsed
            })
            time.sleep(1)
    return rows

def summarise(rows):
    print(f"{'Model':38}{'Exact':>7}{'Failed':>8}{'Tokens':>9}{'Cost $':>10}")
    print("-"*72)
    for _,model in MODELS:
        mine=[r for r in rows if r["model"]==model]
        exact=sum(1 for r in mine if r["exact"])
        failed=sum(1 for r in mine if r["failed"])
        toks=sum(len(r["corrupted"].split())+len(r["corrected"].split()) for r in mine)
        print(f"{model:38}{exact:>7}{failed:>8}{toks:>9}{0.0:>10.5f}")

def summarise_error_types(rows):
    error_types = ["kaz_to_rus","latin_homoglyph","drop_hyphen","join_words","double_letter"]
    models = [m for _,m in MODELS]
    print("\nWhich error types did each model repair?")
    print(f"{'Error type':15}" + "".join(f"{m:>12}" for m in models))
    print("-"*(15+12*len(models)))
    for err in error_types:
        row = f"{err:15}"
        for m in models:
            mine=[r for r in rows if r["model"]==m]
            flags=[ch for r in mine for ch in r.get("changes",[]) if err in ch.lower()]
            if len(flags)==0:
                val="no"
            elif len(flags)==len(mine):
                val="yes"
            else:
                val="partial"
            row += f"{val:>12}"
        print(row)

# --- MAIN ---
if __name__=="__main__":
    out=run_all()
    summarise(out)            # первая таблица
    summarise_error_types(out) # вторая таблица
