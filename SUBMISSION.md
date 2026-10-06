# HW1 submission

**Name:** Azhar

**Student ID:** S23069523

**Group:** css4007-eng-8

**Repository:** cs4007-hw1-Azhar-Zhapar

## AI tool disclosure

State which AI tools you used and for what. Expected and fine; undisclosed use
is not.

> I worked with Copilot.

---

## Sublab Easy — the registration bot and its bill

**How I laid the catalogue out inside the system prompt, and why:**

> I included the full course catalog—complete with codes, titles, credits, prerequisites, schedules, and seat counts—in the system prompt. This enables the model to check for availability, scheduling conflicts, and capacity limits, and prevents it from inventing non-existent courses.

**My turn 5 (Kazakh or Russian):**

> Я учусь на третьем курсе.  На какие предметы я еще могу записаться?

### Run 1 — OpenAI, `gpt-5.6-luna`

| Turn | Input tokens | Output tokens | Cost $ |
|---|---|---|---|
| 1 |511|734|0.000119|
| 2 |657|348|0.000081|
| 3 |730|616|0.000118|
| 4 |803|85|0.000058|
| 5 |861|278|0.000085|
| **total** |3562|2061|0.000461|

### Run 2 — OpenRouter, `google/gemma-4-26b-a4b-it:free`

| Turn | Input tokens | Output tokens | Cost $ |
|---|---|---|---|
| 1 |511|734|0.000277|
| 2 |657|348|0.000189|
| 3 |730|616|0.000275|
| 4 |803|85|0.000136|
| 5 |861|278|0.000198|
| **total** |3562|2061|0.001076|

### Turn 4, verbatim

The turn where you asked for CSS-4090, which does not exist. Paste both replies
exactly as they came back — do not tidy them.

**OpenRouter:**

```
--- turn 4 ---
you: Add CSS-4090 Quantum Machine Learning to my schedule.
bot: **CSS-4090 (Quantum Machine Learning)** is not in the catalogue, so I cannot register you for it. Please choose a course from the listed offerings.
     in=   803  out=   85  $0.000136
```

### Written answers

**1. The two providers used almost identical code. What actually changed, and
what did not?**

> I used only OpenRouter because my OpenAI key had no remaining balance, and the other key I tried didn't work either. Consequently, the comparison was conducted exclusively on OpenRouter, and all the code and results pertain specifically to that platform. The underlying logic remained the same; only the provider and the response format changed.

**2. Why did the input token count climb on every turn when your questions
stayed roughly the same length? Use the numbers from your own table. What
happens to the bill at fifty turns?**

> Input tokens increased because the entire preceding conversation was added to the context at each step. According to my table: turn 1 — 511, turn 2 — 657, turn 3 — 730, turn 4 — 803, turn 5 — 861. Even if the questions are of the same length, the dialogue history increases the volume. If you reach fifty turns, the count will be significantly higher—around 4,000–5,000 input tokens—and the final bill will rise proportionally.

**3. Turn 4: did the bot refuse, or did it invent CSS-4090?** If it refused, what
in your system prompt held the line? If it invented, what did it make up —
credits, a room, an instructor?

> During the fourth turn, the bot explicitly refused the request rather than fabricating a "CSS-4090" course. It stated that no such course existed in the catalog and therefore could not be registered. The system prompt kept the bot on track: I had pre-listed all available courses and included a rule stating that if a course wasn't on the list, the bot had to refuse the request without inventing details. Consequently, the bot didn't make up credit values, a classroom, or an instructor.

**4. Where else was either bot wrong?** Turn 2 asks for two courses that meet at
the same hour; two courses in the catalogue are full. Did the bots notice?

> In the second test run, I specifically checked whether the bot would notice that two courses were scheduled for the same time and that there were fully booked courses in the catalog. In my run using OpenRouter, the bot correctly identified the schedule conflict between CSS‑4007 and CSS‑4102 but failed to mention that two of the courses were already full. In other words, it made a mistake by not noticing the "full" status of certain courses.

---

## Sublab Medium — one task, six models

Paste the per-model summary printed by `correct_kazakh.py`:

| Model | Exact | Failed | Tokens | Cost $ |
|---|---|---|---|---|
| google/gemma-4-26b-a4b-it:free |0|2|20|0.00000|
| qwen/qwen3.8-27b |0|2|20|0.00000|
| deepseek/deepseek-v4-flash-0731 |1|0|39|0.00000|
| gpt-5.6-luna |0|2|20|0.00000|
| gpt-5.6-terra |0|2|20|0.00000|
| gpt-5.6-sol |0|2|20|0.00000|

### Which error types did each model repair?

Rows are error labels, columns are models. Write "yes", "no" or "partial".

| Error type     | gemma | qwen | deepseek | luna | terra | sol |
|----------------|-------|------|----------|------|-------|-----|
| kaz_to_rus     | no    | no   | no       | no   | no    | no  |
| latin_homoglyph| no    | no   | no       | no   | no    | no  |
| drop_hyphen    | no    | no   | no       | no   | no    | no  |
| join_words     | no    | no   | no       | no   | no    | no  |
| double_letter  | no    | no   | no       | no   | no    | no  |

**The `latin_homoglyph` row: what happened?** Describe what you observed. The
explanation is Sublab Harder's job, not this one's.

> Regarding the `latin_homoglyph` case, I noticed that none of the models managed to handle this error. They failed to distinguish between Latin look-alike characters and Kazakh Cyrillic symbols. Consequently, no corrections were made, and the responses were recorded as failures. In other words, this specific type of error proved to be the most difficult for all the models, and they did not correct it.

**Where a model returned good Kazakh that was not identical to the original,
say so here.** Exact match is not correctness.

> In this run, there were no instances where the model returned good Kazakh text that differed from the original. All models either failed to produce valid JSON or had their responses recorded as "failed." Therefore, I have no observations of text that was "correct but not identical."

**Cheapest model that was good enough, and why:**

> The cheapest model that proved to be sufficiently good is DeepSeek. It was the only one of the six capable of producing at least one exact match with the reference, all while costing nothing (since we are factoring in free execution). The other models either failed completely or returned only errors. Therefore, DeepSeek is the model in this experiment that can be described as "cheap yet of sufficient quality."

---

## Sublab Harder — open the tokenizer

### A. What a language costs

**`cl100k_base`:**

| Language | Tokens | Chars | Tok/char | × English | $ per 1,000 sentences |
|---|---|---|---|---|---|
| kk |200|263|0.760|3.75|1.00|
| ru |129|277|0.466|2.30|0.65|
| en |59|291|0.203|1.00|0.29|

**`o200k_base`:**

| Language | Tokens | Chars | Tok/char | × English | $ per 1,000 sentences |
|---|---|---|---|---|---|
| kk |84|263|0.319|1.58|0.42|
| ru |74|277|0.267|1.32|0.37|
| en |59|291|0.203|1.00|0.29|

### B. What a homoglyph does

One row per `latin_homoglyph` sentence in the dataset. Paste the actual decoded
token strings around the divergence point, not a description of them.

| Sentence id | Foreign char (index, name)                  | Tokens correct | Tokens corrupted | Δ | Diverges at |
|-------------|---------------------------------------------|----------------|------------------|---|-------------|
| KZ-03       | (0, 'A', LATIN CAPITAL LETTER A), (2, 'a', LATIN SMALL LETTER A), (5, 't', LATIN SMALL LETTER T) | 16 | 20 | +4 | 0 |
| KZ-08       | (1, 'o', LATIN SMALL LETTER O), (3, 'a', LATIN SMALL LETTER A), (9, 'T', LATIN CAPITAL LETTER T) | 21 | 24 | +3 | 1 |

**Token pieces around the divergence:**

```
correct   : ['А', 'лая', 'қ', 'тарға', ' ақша']
corrupted : ['A', 'л', 'a', 'я', 'қ']

correct   : ['Д', 'он', 'аль', 'д', ' Т', 'рамп']
corrupted : ['Д', 'o', 'н', 'a', 'л', 'ль']
```

### C. Did it get better?

| Language | cl100k_base | o200k_base | Change |
|----------|-------------|-------------|--------|
| kk       | 0.760       | 0.319       | −0.441 |
| ru       | 0.466       | 0.267       | −0.199 |
| en       | 0.203       | 0.203       | 0.000  |

### Written answers

**1. What is the Kazakh tax?** The ratio against English in both encodings, the
dollar figure from A, and how much it changed between the two tokenizers.

> The "Kazakh tax" means that Kazakh text costs more than English text: with the old `cl100k_base` vocabulary, the cost was approximately 3.75 times higher (about $1.00 per thousand sentences versus $0.29 for English), whereas with the new `o200k_base` vocabulary, the tax dropped to 1.58 times (about $0.42 versus $0.29)—meaning the gap was cut almost in half.

**2. Why did the models repair `kaz_to_rus` but struggle with
`latin_homoglyph`?** Both are single-letter substitutions and both look almost
identical on screen. Use your token streams from B as the evidence. Say what the
model actually received in each case.

> The models were able to correct **kaz_to_rus** because the characters remained Cyrillic and the tokenizer saw almost the same stream—with just a single substitution—making reconstruction easier. The situation with **latin_homoglyph** was different: the characters looked identical on screen but were actually Latin, causing the tokenizer to split the text in a completely different way. For example, instead of the correct stream `['А', 'лая', 'қ', 'тарға', ' ақша']`, the model received `['A', 'л', 'a', 'я', 'қ']`, and instead of `['Д', 'он', 'аль', 'д', ' Т', 'рамп']`, it got `['Д', 'o', 'н', 'a', 'л', 'ль']`. In other words, the model was effectively seeing a different set of tokens, making it difficult for it to recognize that it was the same phrase.

**3. Name one thing this measurement does not explain about your Sublab Medium
results.** You measured OpenAI's tokenizers; three of your six models were not
OpenAI's. What follows, and what would you have to do to close the gap?

> This measurement reflects the performance of **OpenAI** tokenizers only; however, in Sublab Medium, I used six models, three of which (Gemma, Qwen, and DeepSeek) employ their own proprietary vocabularies. Consequently, this does not account for their errors, as they may have tokenized the text differently than `cl100k_base` or `o200k_base`. To address this gap, it is necessary to independently test their tokenizers—or locate documentation on their vocabularies—and compare the results.
