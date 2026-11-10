# MYP Mathematics 5 — Answer-Key Audit

Method: full text extracted per PDF page (`rewrite/extracts/full_mypy5.txt`, answer key at
PDF p258; `@@PAGE n@@` marker = doc[n−1] = book page n−13). Every numeric claim in the answer
key recomputed independently from the question bodies; candidates confirmed against raw
`pymupdf` text **and** rendered pages (2.8× zoom; 7–8× crops for small digits) before being
flagged. Raw dumps silently drop radicals and some exponents, so nothing was flagged on a raw
dump alone.

## Verdict: 7 answer-key errors (Ch3 ×1, Ch7 ×5, Ch11 ×1 minor) + 2 self-flagged body defects.

### Ch1–6 (1 error)
- **3B Q7** — key prints 1.48661 / 2973.22; true values from the body data: 1.48780 / 2975.61.

### Ch7 (5 errors)
- **Mixed 7, Q3** — key prints a² = 64.49; true value 79.98.
- **Mixed 7, Q4** — key prints cos A = 16/84; true value 4/84.
- **Mixed 7, Q15** — key prints 4√2 (true 8√2), l = 12.2 (true 15.1), α = 60.5° (true 41.5°).
- **Mixed 7, Q18** — key's AF/BF ranges (7.717–8.099 / 6.495–6.935) and the 0.289 km shift
  do not reproduce from the body geometry; recomputation gives different values.
- **Criterion D, Q5** — key prints L = 0.14, LC = 3.92, total 7.10; true values 0.09 / 3.98 / 7.16.

### Ch8 — 0 errors (closed, fully verified)
All exercises, mixed practice and criterion tasks recompute as printed. Spot values:
8B Q9 k = 4, −3; 8D Q3 AB ≠ BA; Mixed 8 Q20 A⁻¹ = (1 −1; −1 2); CA (10, −11);
CB Sₙ = (1 0; n 1); Crit C R = (0 −1; 1 0); Crit D 37,500 m².

### Ch9 — 0 errors (closed, fully verified)
Spot values: 9C IQR 6, fence 23.5 (25 is the outlier); 9D Q3 r = 0.970;
Ex 9.10 ŷ = −0.0514 + 0.1696x, R² = 0.9502; 9E Q6 r = −0.849; Mixed 9 Q15 r = 0.995;
Modelling r = 0.971, b = 2.7381; CB r 0.776 → 0.825 after removing (10, 18);
CD x̄ = 4.5, ȳ = 11.925, r = −0.958.
- **CA Q3 investigated and cleared** (candidate false alarm, my own arithmetic slip):
  body data 0<t≤10: 6; 10<t≤20: 14; 20<t≤30: 8; 30<t≤40: 2 → midpoints 5, 15, 25, 35;
  Σf = 30, Σfx = 510, Σfx² = 10750, x̄ = 17, s² = 69.3, s = 8.33 — exactly as printed. Key correct.

### Ch10 — 0 errors (closed, fully verified)
Opener 26.9%; Ex 10.8 15/56 … 25/28; Inv 10 threshold n = 23, E = 0.693;
Modelling 190/1584 → 10.7%; CA 13/20; CB 10/9; CD 135/332 ≈ 40.7%.

### Ch11 (1 minor key flag + 2 self-flagged body defects)
- **Milestone Q4** — key: "10-year payback ≈ £3.67/m³". 3.67 = 900/(10 × 24.512), i.e. it
  divides by 10 **terms**; a 10-**year** horizon gives ≈ £0.92–1.22. Minor (wording/units).
- Body defect 1: prerequisites section labels a 2×2 matrix array "3×3".
- Body defect 2: 11.4 GP Q2 working hint prints "900 − 4a"; correct hint "900 + 4a".
- Otherwise key and body match throughout (docs 229–243). Spot values: 11A 7.69% / 8.3%,
  6.7×; 11C ŷ = 115.5 + 7.42t, day 12 → 205; 11D 2500 / 2484 / 2400, x = 15, A = 450;
  Ex 11.5 97 mm, 13 weeks; Milestone 26,384 L → 90.2%, 24,512 → 83.8%.

### Ch12 — 0 errors (closed, fully verified)
Opener f(n) = 2ⁿ⁺² − 3 (f(1)=5, f(2)=13, f(3)=29, diffs 4/8/16). 12A Q1–25 incl. Ex 12.3
(BC = √129 = 11.36, B = 22.4°, C = 37.6°); 12B Q1–4 (PB 18, AB 10; 9.43 km; 13 cm, 67.4°);
12C Q1–15 (Q4: 4 red/6 blue → P(RR) = (4/10)(3/9) = 2/15 ≈ 0.133; Ex 12.5 uₙ = 2ⁿ − 1;
Q13 table 24/18/42, 36/42/78); 12D Q1–8 (Q6: 2^(1/8)−1 = 9.05% vs ln2/8 = 8.66%;
Q7: P(TTH) = 1/8 → E = 0.625 vs fee 2 → −1.375, not fair); Criterion A Q1–6
((x−2)(2x−1)(x+3), self-inverse (y+3)/(2y−1), 2.59, S₂₅ = 1225, c = 7.24, area 24.8,
0.325 ≠ 0.275); Criterion B/C/D bodies (f(0…5) = 3, 6, 11, 18, 27, 38 → f = x²+2x+3,
f(10) = 123; Crit C r² = 56%; Crit D 11.1 d, 9th day, 2070 L/d, 8th day).
- Self-flagged body defect: Crit D preamble says the tank is "refilled at a constant rate"
  while the solution models an 1800 L/d **drain**.

## Process notes
- One candidate flag (Ch9 CA Q3: I initially computed mean 16.5 / s 9.28) was my own
  arithmetic slip — the key is correct (see Ch9 above). Lesson logged: recompute body data ×
  midpoints from raw text before flagging a key/body mismatch.
- Radical/exponent drop-out in raw dumps (e.g. "314.8 ÷ 8 = 6.3" is √(314.8/8) = 6.3 as
  printed) — render before flagging.
