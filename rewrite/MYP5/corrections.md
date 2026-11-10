# MYP Mathematics 5 — Corrections (verified errors only)

Re-verification pass (final): every candidate was re-derived from the question body and
confirmed against the rendered page (2.8×; 7–8× crops for the Q15 fraction work).
**Result: 5 genuine errors.** Two earlier audit flags were investigated and cleared —
Mixed 7 Q18 (the key is correct; see "Cleared" below) and Ch9 CA Q3 (audit file).

Each entry gives the exact printed text (book page), the corrected text, and the
verification. Copy the "replace with" text verbatim.

---

## C1 · Chapter 3, Exercise 3B, Q7 (book p261)

**Printed:**
> 7 The student has replaced e by 2.7 before exponentiating, which changes the base:
> 2.7^0.4 = 1.48661 while e^0.4 = 1.49182. The correct value is 2000e^0.4 = 2983.65; the
> substitution gives 2973.22, an error of about 10 because the rounding is amplified by
> the exponent.

**Replace with:**
> 7 The student has replaced e by 2.7 before exponentiating, which changes the base:
> 2.7^0.4 = 1.48780 while e^0.4 = 1.49182. The correct value is 2000e^0.4 = 2983.65; the
> substitution gives 2975.61, an error of about 8 because the rounding is amplified by
> the exponent.

**Verification:** ln 2.7 = 0.993252; ×0.4 = 0.397301; e^0.397301 = 1.487806 (printed
1.48661 is wrong). 2000 × 1.487806 = 2975.61 (printed 2973.22 is wrong). 2000e^0.4 =
2983.65 ✓ as printed; the true difference is 2983.65 − 2975.61 = 8.04 ≈ 8 (printed
"about 10" follows from the wrong 2973.22).

---

## C2 · Chapter 7, Mixed Practice 7, Q3 (book p287)

**Printed:**
> 3 SAS: a² = 9.5² + 7.2² − 2(9.5)(7.2) cos 63° = 64.49, a = 8.94 cm.

**Replace with:**
> 3 SAS: a² = 9.5² + 7.2² − 2(9.5)(7.2) cos 63° = 79.98, a = 8.94 cm.

**Verification:** 9.5² + 7.2² = 142.09; 2 × 9.5 × 7.2 × cos 63° = 136.8 × 0.453990 =
62.106; a² = 142.09 − 62.106 = 79.98. The printed a = 8.94 is consistent with 79.98
(√79.98 = 8.943), so only the intermediate a² is wrong (64.49).

---

## C3 · Chapter 7, Mixed Practice 7, Q4 (book p287)

**Printed:**
> 4 The largest angle faces 9 cm: cos A = (6² + 7² − 9²) / (2(6)(7)) = 16/84 = 0.1905,
> A = 87.3°.

**Replace with:**
> 4 The largest angle faces 9 cm: cos A = (6² + 7² − 9²) / (2(6)(7)) = 4/84 = 0.0476,
> A = 87.3°.

**Verification:** 36 + 49 − 81 = 4 (not 16); 4/84 = 0.04762; arccos(0.04762) = 87.27°
≈ 87.3°, so the printed angle is already correct and the numerator/decimal are typos.

---

## C4 · Chapter 7, Mixed Practice 7, Q15 (book p287)

**Body:** "A square pyramid has base side 16 m and vertical height 10 m. Find a sloping
edge, its angle with the base, and the dihedral angle between a face and the base."

**Printed:**
> 15 Half-diagonal = 4√2 = 5.66 m, so l = √(10² + (4√2)²) = √150 = 5√6 = 12.2 m and
> tan α = 10/(4√2) = 1.7678, α = 60.5°. The dihedral angle uses the apothem 8 m and slant
> height √(10² + 8²) = √164 = 12.8 m: tan β = 10/8 = 1.25, β = 51.3°.

**Replace with:**
> 15 Half-diagonal = 8√2 = 11.31 m, so l = √(10² + (8√2)²) = √228 = 2√57 = 15.1 m and
> tan α = 10/(8√2) = 0.8839, α = 41.5°. The dihedral angle uses the apothem 8 m and slant
> height √(10² + 8²) = √164 = 12.8 m: tan β = 10/8 = 1.25, β = 51.3°.

**Verification:** base 16 m → half-diagonal ½·16√2 = 8√2 = 11.314 m (printed 4√2 is the
value for an 8 m base). l = √(100 + 128) = √228 = 15.0997 ≈ 15.1 m (the printed chain is
internally inconsistent too: √(10² + (4√2)²) = √132, not √150). tan α = 10/11.3137 =
0.88388 → α = 41.48° ≈ 41.5°. The dihedral part is correct as printed (apothem 8 = 16/2,
confirming the 16 m base) and is unchanged.

---

## C5 · Chapter 7, Criterion D "A coastal survey", Q5 (book p289)

**Printed (middle of entry 5):**
> … so L moves from (2.84, 1.51) to (2.85, 1.42) — a shift of 0.14 km, about 140 m;
> opposite-signed errors shift it less, so the position is reliable to about ±0.15 km.
> Then LC = 3.92 km and the journey is 7.10 km in 17.0 minutes, so neither distance nor
> plan changes materially. …

**Replace that span with:**
> … so L moves from (2.84, 1.51) to (2.85, 1.42) — a shift of 0.09 km, about 90 m;
> opposite-signed errors shift it up to about 0.11 km, so the position is reliable to
> about ±0.12 km. Then LC = 3.92 km and the journey is 7.10 km in 17.0 minutes, so
> neither distance nor plan changes materially. …

**Verification:** the printed coordinates are correct (AL = 4.2 sin 46.5°/sin 107° =
3.1858 km along 063.5° → (2.851, 1.422); original L = (2.840, 1.510)); the distance
between them is √(0.011² + 0.089²) = 0.089 km ≈ 0.09 km, not 0.14. Checking all four
±1.5° combinations: shifts 0.089, 0.092 (same-signed) and 0.113, 0.113 km
(opposite-signed) — so opposite-signed errors shift L *more*, and the reliability bound
is about ±0.12 km, not ±0.15. The rest of the entry (LC = 3.92, 7.10 km, 17.0 min) is
correct as printed.

---

## Cleared — Chapter 7, Mixed Practice 7, Q18 (book p287)

**No change required.** An earlier audit pass flagged this entry; full re-derivation
shows the key is correct.

Question: "The opening fire is located from bearings 040° and 330°. If each bearing could
be wrong by 1.5°, estimate how far the calculated position could move. Does the nearer
tower change?" (Towers are the modelling task's, 8 km apart; AF = 7.37 km, BF = 6.52 km
nominally.)

Re-derivation of the four ±1.5° combinations (angles at A: 48.5°/51.5°; at B:
58.5°/61.5°): AF spans 7.133–7.638 km and BF 6.265–6.802 km (key: "7.13 to 7.64" and
"6.27 to 6.80" ✓); position shifts are 0.223, 0.231 km (same-signed) and 0.306, 0.330 km
(opposite-signed) — key: "up to 0.22 km … up to 0.33 km" ✓ within estimation tolerance;
BF < AF in every case, so the nearer tower does not change ✓.

**Minor note (not an error):** the other same-signed case gives 0.231 km, so "up to 0.22
km" is a hair low; "up to about 0.23 km" would be tidier. Acceptable as printed since the
question asks for an estimate. Recorded here so the item is not re-flagged.

---

## Running total after this pass

MYP5 verified errors: **5** (3B Q7; Mixed 7 Q3, Q4, Q15; Crit D Q5) — down from 7 after
the Q18 flag was cleared. Series total: MYP1 2 + MYP5 5 = **7 answer-key errors** across
the five books (plus 2 self-flagged MYP5 body defects: the "3×3" label over a 2×2 array
in Ch11 prerequisites, and the 11.4 GP Q2 hint "900 − 4a" which should read "900 + 4a").
