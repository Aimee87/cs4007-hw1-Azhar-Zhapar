# -*- coding: utf-8 -*-
import tiktoken

def check_word_or_sentence(text: str):
    encodings = ["cl100k_base", "o200k_base"]
    for enc_name in encodings:
        enc = tiktoken.get_encoding(enc_name)
        ids = enc.encode(text)
        tok_per_char = len(ids) / len(text) if text else 0.0
        print(f"\nEncoding: {enc_name}")
        print(f"Text: {text}")
        print(f"Chars: {len(text)}")
        print(f"Tokens: {len(ids)}")
        print(f"Tok/char: {tok_per_char:.3f}")
        print(f"Pieces: { [enc.decode([i]) for i in ids] }")

if __name__ == "__main__":
    # Примеры слов и предложений
    check_word_or_sentence("Қазақстан")              # казахское слово
    check_word_or_sentence("Россия")                 # русское слово
    check_word_or_sentence("Kazakhstan")             # английское слово
    check_word_or_sentence("Мен университетте оқимын.")  # казахское предложение
    check_word_or_sentence("Я учусь в университете.")    # русское предложение
    check_word_or_sentence("I study at university.")     # английское предложение