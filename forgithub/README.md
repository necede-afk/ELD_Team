# Do Now Image Batch — ELD 1,2 and ELD 3,4

Batch-generates the remaining classroom picture prompts with **gpt-image-2**.

**130 images to generate. 10 deliberately excluded.**
Already-generated images are skipped automatically, so the real number is lower.

---

## FILES

| | |
|---|---|
| `manifest.json` | all 140 slots — filename, scene, course, week, day, exclusion flags |
| `style_prompt.txt` | the master style prompt, **sent with every single call** |
| `generate_images.py` | the batch script |
| `generation_log.jsonl` | written as it runs — one line per image |
| `ELD 1-2/` `ELD 3-4/` | output folders, created on first run |

---

## RUN IT

```bash
pip install openai

# 1. See what it would do. Costs nothing.
python generate_images.py --dry-run

# 2. THE TEST. Make five, check them, decide.
python generate_images.py --limit 5

# 3. The rest.
python generate_images.py
```

**It is resume-safe.** It skips any file that already exists, so you can stop it, run it again,
delete bad images and re-run — it only ever makes what is missing.

**Useful flags**

```bash
--course ELD12     # one course at a time
--limit 20         # small batches
--sleep 3          # slower, if you hit rate limits
```

---

## ⚠ BEFORE THE FULL RUN — the credits question

There are **three separate billing surfaces** and they are not interchangeable:

1. **ChatGPT Plus plan caps** — the by-hand route
2. **Codex image credits** — OAuth through the existing ChatGPT login
3. **API billing** — needs `OPENAI_API_KEY` and billing enabled

**Run `--limit 5` first and watch which one gets charged.** If Codex OAuth covers image generation,
the batch is effectively free. If it demands an API key, it is roughly **$0.08–0.19/image →
about $11–25 for 130.**

⚠ Some tools support Codex OAuth for *text* models but not for images, returning
*"No API key found for provider openai."* If that happens, set `OPENAI_API_KEY` and it bills the
API instead. One test settles it.

---

## ⚠ THE TEN EXCLUSIONS — do not batch these

The script skips them automatically. They are flagged in `manifest.json`.

### 📷 REAL PHOTOGRAPHS — take with a phone, no AI
| File | What |
|---|---|
| `ELD12_Wk01_Day01_Mon.png` | Room 150 door — **the sign is the point** |
| `ELD12_Wk03_Day11_Mon.png` | Room 150 interior |
| `ELD12_Wk03_Day14_Thu.png` | Hoover campus map, if the front office has one |

### ✏️ TEXT-BEARING BY DESIGN — the text IS the lesson
Generate these by hand **without** the style prompt. Sending the no-text rule destroys exactly what
makes them work.

| File | What |
|---|---|
| `ELD12_Wk01_Day02_Tue.png` | *welcome* in five scripts — ⚠ verify every spelling |
| `ELD12_Wk02_Day10_Fri.png` | blank school form with field labels |
| `ELD34_Wk01_Day04_Thu.png` | labelled campus map |

### ✅ ALREADY MADE / ♻️ REUSES — copy, do not generate
| File | Use instead |
|---|---|
| `ELD34_Wk01_Day03_Wed.png` | `ELD34_Day1_CommunityGarden.png` |
| `ELD34_Wk18_Day87_Fri.png` | `ELD34_Day87_Mural.png` |
| `ELD12_Wk06_Day29_Fri.png` | `ELD12_Wk06_Day25_Mon.png` |
| `ELD12_Wk09_Day44_Fri.png` | `ELD12_Day1_FindingASeat.png` |
| `ELD34_Wk09_Day44_Fri.png` | `ELD34_Day1_CommunityGarden.png` |

---

## WHY BATCHING IS BETTER THAN BY-HAND

Not just faster. **The full style prompt goes with every single call.**

By hand, the written-language rule fades from context — by image 40 it has stopped holding and text
starts creeping back in. An API loop cannot drift. Same rule, image 1 and image 130.

**What you lose is QC in the loop.** You will not catch failures until the audit.

---

## AUDIT — the part that matters

**Check at FULL SIZE, not thumbnails.** Lettering hides where the eye skips: card labels, book
spines, wall posters, packaging, clock faces, shirt graphics.

- [ ] **No letters or numerals anywhere** — any letterform means delete and re-run
- [ ] Hands and faces clean — count fingers on foreground figures
- [ ] Every face rendered; no smudged middle-distance crowd
- [ ] Cultural plurality per the style; hijab present and natural
- [ ] Emotionally safe — no distress, no poverty spectacle
- [ ] Readable at 3 inches wide (Do Now images print small)
- [ ] Panel images are ONE artwork internally divided, not a grid of thumbnails

**Delete failures and re-run the script.** It regenerates only what is missing.

---

## NAMING — do not change it

```
ELD34_Wk11_Day49_Mon.png
└─┬─┘ └─┬─┘ └──┬─┘ └┬┘
course  week  day#  weekday
```

Sorts course → week → day. The day number is unique across all 87 days, so a file can never be
ambiguous. **The placement script matches on this pattern** — a renamed file will be silently
skipped.

---

## AFTER GENERATION

Copy the two folders into:

```
Claude Workspace/Classroom Docs/ELD/Fall 2026/Do Now Images/
```

Then the placement script inserts them into the slide decks.

⚠ **The lock-down rule:** once a deck has images placed, it is the source of truth and does not get
regenerated. The placement script must refuse to touch a deck that already contains pictures.
