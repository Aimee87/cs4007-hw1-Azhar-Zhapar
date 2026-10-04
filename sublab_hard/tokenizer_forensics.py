# -*- coding: utf-8 -*-
import json, unicodedata
from pathlib import Path
import tiktoken

DATA = Path(__file__).resolve().parent.parent / "data"
PARALLEL = DATA / "parallel.json"
KAZAKH_ERRORS = DATA / "kazakh_errors.json"

ENCODINGS = ["cl100k_base", "o200k_base"]
LANGS = ["kk", "ru", "en"]

def load_triplets():
    return json.loads(PARALLEL.read_text(encoding="utf-8"))["triplets"]

def load_sentences():
    return json.loads(KAZAKH_ERRORS.read_text(encoding="utf-8"))["sentences"]

def encode(text, enc_name):
    enc = tiktoken.get_encoding(enc_name)
    return enc.encode(text)

def pieces(ids, enc_name):
    enc = tiktoken.get_encoding(enc_name)
    return [enc.decode([i]) for i in ids]

def tokens_per_char(text, ids):
    return len(ids)/len(text) if text else 0.0

def first_divergence(a,b):
    for i,(x,y) in enumerate(zip(a,b)):
        if x!=y: return i
    if len(a)!=len(b): return min(len(a),len(b))
    return None

def foreign_chars(text):
    out=[]
    for i,ch in enumerate(text):
        if ch.isalpha():
            name=unicodedata.name(ch,"")
            if "CYRILLIC" not in name:
                out.append((i,ch,name))
    return out

def language_table(enc_name):
    enc=tiktoken.get_encoding(enc_name)
    triplets=load_triplets()
    totals={lang:{"tokens":0,"chars":0} for lang in LANGS}
    for trip in triplets:
        for lang in LANGS:
            text=trip[lang]
            ids=enc.encode(text)
            totals[lang]["tokens"]+=len(ids)
            totals[lang]["chars"]+=len(text)
    for lang in LANGS:
        c=totals[lang]["chars"]
        t=totals[lang]["tokens"]
        totals[lang]["tok_per_char"]=t/c if c else 0.0
    return totals

def cost_per_thousand(tok_per_char, chars, rate_in=5.0):
    tokens_per_sentence=tok_per_char*chars
    tokens_total=tokens_per_sentence*1000
    return (tokens_total/1_000_000)*rate_in

def homoglyph_report(corrupted, correct, enc_name):
    ids_cor=encode(corrupted,enc_name)
    ids_ok=encode(correct,enc_name)
    div=first_divergence(ids_cor,ids_ok)
    return {
        "foreign":foreign_chars(corrupted),
        "tokens_correct":len(ids_ok),
        "tokens_corrupted":len(ids_cor),
        "delta":len(ids_cor)-len(ids_ok),
        "diverge_at":div,
        "pieces_correct":pieces(ids_ok,enc_name),
        "pieces_corrupted":pieces(ids_cor,enc_name)
    }

# --- MAIN ---
if __name__=="__main__":
    print("=== A. What a language costs ===")
    for enc_name in ENCODINGS:
        table=language_table(enc_name)
        print(f"\n{enc_name}:")
        print("lang   tokens   chars   tok/char   ×English   $/1000 sentences")
        base=table["en"]["tok_per_char"]
        for lang in LANGS:
            row=table[lang]
            ratio=row["tok_per_char"]/base if base else 0.0
            cost=cost_per_thousand(row["tok_per_char"],row["chars"])
            print(f"{lang:4} {row['tokens']:7} {row['chars']:7} {row['tok_per_char']:9.3f} {ratio:9.2f} {cost:17.2f}")

    print("\n=== B. What a homoglyph does ===")
    rows=[r for r in load_sentences() if "latin_homoglyph" in r["errors"]]
    for row in rows:
        rep=homoglyph_report(row["corrupted"],row["correct"],"o200k_base")
        print(f"\nSentence {row['id']}: Δ={rep['delta']} tokens ({rep['tokens_correct']} -> {rep['tokens_corrupted']}), diverge at {rep['diverge_at']}")
        for idx,ch,name in rep["foreign"]:
            print(f"  char {idx} is {ch!r} - {name}")
        d=rep["diverge_at"] or 0
        print("  correct   :",rep["pieces_correct"][max(0,d-1):d+5])
        print("  corrupted :",rep["pieces_corrupted"][max(0,d-1):d+5])

    print("\n=== C. Did it get better? ===")
    old,new=(language_table(e) for e in ENCODINGS)
    for lang in LANGS:
        print(f"{lang:4}: {old[lang]['tok_per_char']:.3f} -> {new[lang]['tok_per_char']:.3f} (change {old[lang]['tok_per_char']-new[lang]['tok_per_char']:+.3f})")
