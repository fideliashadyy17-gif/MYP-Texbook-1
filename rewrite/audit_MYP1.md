# MYP Mathematics 1 — Answer-Key Audit

Method: full text extracted per PDF page (`rewrite/extracts/full_mypy1.txt`, answer key at
PDF p216), every numeric claim in the answer key recomputed independently from the question
bodies; candidates confirmed only against raw `pymupdf` page text **and** rendered pages
(3× zoom) before being flagged.

## Verdict: 2 errors, both minor (Ch1, Ch2). One further candidate investigated and cleared (Ch5).

### Error 1 — Chapter 1, Criterion Task "Museum label": word-count claim
- Printed key: `Sample label (67 words). "The Hall of Numbers opened in 1894. …"`
- The printed label contains **44 words** (rendered page 217 confirmed — the label is
  complete in the text; no reasonable counting rule reaches 67).
- The label itself satisfies the task (≤ 70 words, expanded form, rounded figures,
  comparison); only the parenthetical count is wrong.
- Fix: `Sample label (44 words).` — see `corrections.md`.

### Error 2 — Chapter 2, Investigation 2 "The doubling sheet", Q8
- Printed key: `After 10 folds the ratio is 3¹⁰ ÷ 2¹⁰ = 57,665 ÷ 1,024 ≈ 57.7.`
- 3¹⁰ = **59,049**, not 57,665. The final value ≈ 57.7 is correct (59,049 ÷ 1,024 =
  57.665…), so only the intermediate numerator is a typo.
- Fix: `3¹⁰ ÷ 2¹⁰ = 59,049 ÷ 1,024 ≈ 57.7.`

### Candidate cleared — Chapter 5, Application "The community market stall", Q7
- The key's 7.65 / 3.40 / 4.25 are exactly 15% **off the marked prices** (9.00 / 4.00 /
  5.00), which is the correct reading of "advertise '15% off everything' instead of the
  individual discounts". Revenue £381.65, £13.35 less than £395 — all correct.
- An earlier audit pass misread the discount as applied to the current sale prices and
  flagged this; re-reading the question body cleared it. **Not an error.**

## Chapters verified clean
All remaining chapters' keys (exercises, investigations, applications, criterion tasks,
mixed practice) recomputed with zero discrepancies.
