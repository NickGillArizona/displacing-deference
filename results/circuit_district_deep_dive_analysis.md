# Circuit District Deep-Dive Analysis

Generated: 2026-04-15T23:53:27

## Method and assumptions

- Reused the same screened-in disability universe and the same period definitions as scripts/extended_doctrinal_analysis.py: P1 = 2013-2020, P2 = 2021-2022, P3 = 2023-2026.
- Kept the original broad-win definition: outcome in {PLAINTIFF_WIN, MIXED}.
- Ranked circuits by the full-universe P1 -> P3 broad-win decline, then did the district/judge attribution on district-court cases inside those circuits.
- The unified database has no native district or judge fields. Districts were derived from the structured court field; judges were parsed from opinion headers/signatures in the raw-text opinion files under ../allFHAcases.
- Singleton surnames and obvious OCR fragments are now only counted as identified judges when they can be canonically matched to a fuller identity; otherwise they are pushed into the unresolved bucket so they do not overstate identification coverage or depress the unknown-inclusive HHI.
- District and judge 'decline' shares are expressed as a P3 shortfall count: expected P3 broad wins at the circuit's district-court P1 baseline minus actual P3 broad wins. They locate where the P3 shortfall is concentrated, not whose own P1 -> P3 rate changed the most.
- Share-of-full-decline ratios are diagnostic, non-additive shares rather than partition totals. They can exceed 100% because a district-court shortfall is being compared with a full-circuit denominator while offsetting negative contributions and non-district components remain outside the numerator.
- The district-side >50% test is complete because every P3 district-court case is district-assigned. The judge-side >50% test now reports conservative bounds: observed top identified judge share, unknown-judge share, and the max possible single-judge share if all unresolved judge shortfall belonged to one judge.
- MTD survival is coded as 1 - defendant-win rate among P3 district-court motion-to-dismiss cases.
- Post-Jan.-2025 appointee checks use office-relevant appointment dates when a single federal office can be tied to the judge's case district; same-district multi-office biographies are left unresolved rather than forced into a negative.
- A circuit-level post-Jan.-2025 result is only definitive when both judge identification and appointment lookups are complete; otherwise the result is reported as indeterminate rather than as a clean negative.
- Appointment dates come from manual seeds first, then any prior district-keyed lookup results already cached in results/circuit_district_deep_dive_results.json when that file exists, and only then from live Wikipedia lookups. That makes reruns reproducible within this workspace, but a fresh machine or later Wikipedia edits can still change the unresolved/resolved mix at the margins.

## Table: top-5 declining circuits with district-level decomposition

| Circuit | Full P1→P3 decline | P3 district-court cases | Leading district (identified P3 judges) | District share of full decline | Leading judge | Judge share of full decline | HHI (identified / +unknown) | Post-Jan-2025 appointee check |
| --- | ---: | ---: | --- | ---: | --- | ---: | ---: | --- |
| 2nd Circuit | 48.84% → 8.54% (-40.30 pp) | 157 | S.D.N.Y. (33) | 60.4% | Laura Taylor Swain | 23.6% | 680.73 / 637.35 | 0 resolved; indeterminate |
| 4th Circuit | 46.15% → 10.53% (-35.63 pp) | 85 | D. Md. (13) | 59.9% | Deborah L. Boardman | 8.1% | 508.88 / 851.21 | 0 resolved; indeterminate |
| 10th Circuit | 43.75% → 10.00% (-33.75 pp) | 68 | D. Kan. (5) | 25.4% | Gerald L. Jackson | 11.8% | 528.00 / 986.16 | 0 resolved; indeterminate |
| 5th Circuit | 42.86% → 15.58% (-27.27 pp) | 70 | N.D. Tex. (6) | 35.2% | Susan Hightower | 14.3% | 464.85 / 1767.35 | 0 resolved; indeterminate |
| 3rd Circuit | 45.83% → 24.73% (-21.10 pp) | 84 | E.D. Pa. (11) | 75.1% | Susan D. Wigenton | 21.7% | 621.30 / 1689.34 | 0 resolved; indeterminate |

## Finding: is the decline concentrated in a few judges or genuinely diffuse?

- Districts clearing the >50% full-circuit-decline threshold appear in 3 circuits; there are 4 qualifying district entries: 2nd Circuit — S.D.N.Y. (60.4% of full-circuit shortfall); 4th Circuit — D. Md. (59.9% of full-circuit shortfall); 3rd Circuit — E.D. Pa. (75.1% of full-circuit shortfall); 3rd Circuit — D.N.J. (51.0% of full-circuit shortfall).
- No circuit has a definitive observed >50% single-judge concentration.
- The judge-side >50% full-circuit test resolves to no in: 2nd Circuit (max possible single-judge share 30.6%); 4th Circuit (max possible single-judge share 34.4%); 10th Circuit (max possible single-judge share 38.9%).
- The judge-side >50% full-circuit test remains indeterminate where unresolved judge assignments are too large to rule out a single-judge concentration: 5th Circuit (observed top identified=14.3%, unknown bucket=51.4%, max possible=65.7%); 3rd Circuit (observed top identified=21.7%, unknown bucket=61.5%, max possible=83.2%).
- Judge-concentration HHI ranges from 464.85 to 680.73 on identified judges only, and from 637.35 to 1767.35 when the unknown-judge bucket is treated as one extra chamber.
- Overall, the P3 shortfall is more district-concentrated than judge-concentrated: 4 district entries across 3 circuits clear the >50% full-circuit threshold, while the single-judge test resolves to no in 2nd Circuit, 4th Circuit, and 10th Circuit and remains indeterminate in 5th Circuit and 3rd Circuit.

## Finding: does any post-2025 appointee drive meaningful share of P3 outcomes?

- No resolved judge biography shows a post-Jan.-2025 appointee in the P3 set, but the overall check is indeterminate rather than definitively negative.
- Remaining gaps that prevent a definitive negative: 2nd Circuit (50 unresolved appointment lookups; 10 P3 cases with unidentified judges); 4th Circuit (25 unresolved appointment lookups; 20 P3 cases with unidentified judges); 10th Circuit (26 unresolved appointment lookups; 18 P3 cases with unidentified judges); 5th Circuit (22 unresolved appointment lookups; 28 P3 cases with unidentified judges); 3rd Circuit (4 unresolved appointment lookups; 32 P3 cases with unidentified judges).
- Unresolved appointment lookups alone still total 127 across the five circuits.

## Conclusion: effect on the 'institutional, not ideological' claim

- This deep dive still points most strongly to a district-level pleading gate: the steepest declines are heavily concentrated in a few districts, and those districts tend to pair high P3 pro se shares with very low P3 MTD survival.
- But the no-single-judge and no-post-2025-appointee claims are not fully global. The no-single-judge claim is definitive only in 2nd Circuit, 4th Circuit, and 10th Circuit and remains unresolved in 5th Circuit and 3rd Circuit. The post-2025-appointee check remains indeterminate because some P3 judges still lack office-relevant appointment dates or judge identification.

## Circuit-by-circuit findings

### 2nd Circuit

- Full circuit decline: 48.84% -> 8.54% (-40.30 pp), producing a P3 shortfall of 66.09 broad-win-equivalent cases.
- District-court component: 45.95% -> 7.01% (-38.94 pp), with 61.13 shortfall cases across 157 P3 district-court cases (95.7% of the circuit's P3 docket).
- Largest district shortfall concentrations: S.D.N.Y. (39.95 shortfall cases; 60.4% of full-circuit decline; identified P3 judges=33; P3 pro se=80.00%; P3 MTD survival=16.00%); E.D.N.Y. (10.11 shortfall cases; 15.3% of full-circuit decline; identified P3 judges=11; P3 pro se=68.18%; P3 MTD survival=0.00%); N.D.N.Y. (5.65 shortfall cases; 8.6% of full-circuit decline; identified P3 judges=10; P3 pro se=57.14%; P3 MTD survival=29.41%).
- Largest identified judge shortfall concentrations: Laura Taylor Swain (S.D.N.Y.; 15.62 shortfall cases; 23.6% of full-circuit decline); Rachel P. Kovner (E.D.N.Y.; 2.30 shortfall cases; 3.5% of full-circuit decline); Ronnie Abrams (S.D.N.Y.; 2.30 shortfall cases; 3.5% of full-circuit decline).
- Judge identification coverage: 147 / 157 P3 district-court cases (93.6%).
- Concentration: HHI identified-only=680.73; HHI with unknown bucket=637.35.
- >50% test for full-circuit decline: top district S.D.N.Y. = 60.4%; judge-side result = definitive no; observed top identified judge Laura Taylor Swain = 23.6%, unknown-judge bucket = 7.0%, conservative max possible single-judge share = 30.6%.
- Post-Jan. 2025 appointee check: indeterminate; 0 resolved post-Jan. 2025 appointees found, but 50 identified judges still lack appointment dates and 10 P3 cases still lack judge identification.

### 4th Circuit

- Full circuit decline: 46.15% -> 10.53% (-35.63 pp), producing a P3 shortfall of 33.85 broad-win-equivalent cases.
- District-court component: 54.55% -> 9.41% (-45.13 pp), with 38.36 shortfall cases across 85 P3 district-court cases (89.5% of the circuit's P3 docket).
- Largest district shortfall concentrations: D. Md. (20.27 shortfall cases; 59.9% of full-circuit decline; identified P3 judges=13; P3 pro se=62.00%; P3 MTD survival=23.33%); E.D.N.C. (4.91 shortfall cases; 14.5% of full-circuit decline; identified P3 judges=2; P3 pro se=100.00%; P3 MTD survival=16.67%); D.S.C. (4.36 shortfall cases; 12.9% of full-circuit decline; identified P3 judges=3; P3 pro se=87.50%; P3 MTD survival=25.00%).
- Largest identified judge shortfall concentrations: Deborah L. Boardman (D. Md.; 2.73 shortfall cases; 8.1% of full-circuit decline); Stephanie A. Gallagher (D. Md.; 2.73 shortfall cases; 8.1% of full-circuit decline); Brendan A. Hurson (D. Md.; 2.18 shortfall cases; 6.5% of full-circuit decline).
- Judge identification coverage: 65 / 85 P3 district-court cases (76.5%).
- Concentration: HHI identified-only=508.88; HHI with unknown bucket=851.21.
- >50% test for full-circuit decline: top district D. Md. = 59.9%; judge-side result = definitive no; observed top identified judge Deborah L. Boardman = 8.1%, unknown-judge bucket = 26.3%, conservative max possible single-judge share = 34.4%.
- Post-Jan. 2025 appointee check: indeterminate; 0 resolved post-Jan. 2025 appointees found, but 25 identified judges still lack appointment dates and 20 P3 cases still lack judge identification.

### 10th Circuit

- Full circuit decline: 43.75% -> 10.00% (-33.75 pp), producing a P3 shortfall of 23.62 broad-win-equivalent cases.
- District-court component: 46.67% -> 10.29% (-36.37 pp), with 24.73 shortfall cases across 68 P3 district-court cases (97.1% of the circuit's P3 docket).
- Largest district shortfall concentrations: D. Kan. (6.00 shortfall cases; 25.4% of full-circuit decline; identified P3 judges=5; P3 pro se=40.00%; P3 MTD survival=20.00%); E.D. Okla. (4.67 shortfall cases; 19.8% of full-circuit decline; identified P3 judges=3; P3 pro se=10.00%; P3 MTD survival=NA); D. Utah (4.53 shortfall cases; 19.2% of full-circuit decline; identified P3 judges=5; P3 pro se=57.14%; P3 MTD survival=42.86%).
- Largest identified judge shortfall concentrations: Gerald L. Jackson (E.D. Okla.; 2.80 shortfall cases; 11.8% of full-circuit decline); Eric F. Melgren (D. Kan.; 1.87 shortfall cases; 7.9% of full-circuit decline); Holly L. Teeter (D. Kan.; 1.87 shortfall cases; 7.9% of full-circuit decline).
- Judge identification coverage: 50 / 68 P3 district-court cases (73.5%).
- Concentration: HHI identified-only=528.0; HHI with unknown bucket=986.16.
- >50% test for full-circuit decline: top district D. Kan. = 25.4%; judge-side result = definitive no; observed top identified judge Gerald L. Jackson = 11.8%, unknown-judge bucket = 27.1%, conservative max possible single-judge share = 38.9%.
- Post-Jan. 2025 appointee check: indeterminate; 0 resolved post-Jan. 2025 appointees found, but 26 identified judges still lack appointment dates and 18 P3 cases still lack judge identification.

### 5th Circuit

- Full circuit decline: 42.86% -> 15.58% (-27.27 pp), producing a P3 shortfall of 21.00 broad-win-equivalent cases.
- District-court component: 60.00% -> 15.71% (-44.29 pp), with 31.00 shortfall cases across 70 P3 district-court cases (90.9% of the circuit's P3 docket).
- Largest district shortfall concentrations: N.D. Tex. (7.40 shortfall cases; 35.2% of full-circuit decline; identified P3 judges=6; P3 pro se=71.43%; P3 MTD survival=16.67%); S.D. Tex. (6.00 shortfall cases; 28.6% of full-circuit decline; identified P3 judges=6; P3 pro se=90.00%; P3 MTD survival=20.00%); W.D. Tex. (4.60 shortfall cases; 21.9% of full-circuit decline; identified P3 judges=6; P3 pro se=90.91%; P3 MTD survival=28.57%).
- Largest identified judge shortfall concentrations: Susan Hightower (W.D. Tex.; 3.00 shortfall cases; 14.3% of full-circuit decline); Charles Eskridge (S.D. Tex.; 1.80 shortfall cases; 8.6% of full-circuit decline); David L. Horan (N.D. Tex.; 1.80 shortfall cases; 8.6% of full-circuit decline).
- Judge identification coverage: 42 / 70 P3 district-court cases (60.0%).
- Concentration: HHI identified-only=464.85; HHI with unknown bucket=1767.35.
- >50% test for full-circuit decline: top district N.D. Tex. = 35.2%; judge-side result = indeterminate; observed top identified judge Susan Hightower = 14.3%, unknown-judge bucket = 51.4%, conservative max possible single-judge share = 65.7%.
- Post-Jan. 2025 appointee check: indeterminate; 0 resolved post-Jan. 2025 appointees found, but 22 identified judges still lack appointment dates and 28 P3 cases still lack judge identification.

### 3rd Circuit

- Full circuit decline: 45.83% -> 24.73% (-21.10 pp), producing a P3 shortfall of 19.62 broad-win-equivalent cases.
- District-court component: 53.33% -> 22.62% (-30.71 pp), with 25.80 shortfall cases across 84 P3 district-court cases (90.3% of the circuit's P3 docket).
- Largest district shortfall concentrations: E.D. Pa. (14.73 shortfall cases; 75.1% of full-circuit decline; identified P3 judges=11; P3 pro se=83.78%; P3 MTD survival=9.68%); D.N.J. (10.00 shortfall cases; 51.0% of full-circuit decline; identified P3 judges=11; P3 pro se=63.33%; P3 MTD survival=36.84%); D. Del. (0.73 shortfall cases; 3.7% of full-circuit decline; identified P3 judges=2; P3 pro se=57.14%; P3 MTD survival=33.33%).
- Largest identified judge shortfall concentrations: Susan D. Wigenton (D.N.J.; 4.27 shortfall cases; 21.7% of full-circuit decline); Gerald J. Pappert (E.D. Pa.; 2.20 shortfall cases; 11.2% of full-circuit decline); Esther Salas (D.N.J.; 2.13 shortfall cases; 10.9% of full-circuit decline).
- Judge identification coverage: 52 / 84 P3 district-court cases (61.9%).
- Concentration: HHI identified-only=621.3; HHI with unknown bucket=1689.34.
- >50% test for full-circuit decline: top district E.D. Pa. = 75.1%; judge-side result = indeterminate; observed top identified judge Susan D. Wigenton = 21.7%, unknown-judge bucket = 61.5%, conservative max possible single-judge share = 83.2%.
- Post-Jan. 2025 appointee check: indeterminate; 0 resolved post-Jan. 2025 appointees found, but 4 identified judges still lack appointment dates and 32 P3 cases still lack judge identification.

## Limitations

- Judge parsing depends on OCR quality in the raw opinion texts; district totals are more reliable than judge-name totals where signatures were badly scanned or where orders only exposed docket initials/section numbers.
- The conservative max-possible single-judge share assumes all unresolved judge shortfall could collapse onto one judge; that is the correct bound for the >50% test, but it is intentionally worst-case rather than a point estimate.
- Appointment-date coverage is now strongest for the judges occupying the largest identified shortfall shares; lower-impact magistrate names and judges without stable public biography pages still leave the all-judges census incomplete, and same-district multi-office biographies are treated conservatively as unresolved when the office-relevant appointment date cannot be isolated.
- Because share-of-full-decline uses a full-circuit denominator, district and judge rows should not be added together and should not be read as exhausting the full decline even when an individual row exceeds 100%.
- The appointment-lookup layer is partly path-dependent: if a prior deep-dive JSON exists in this workspace, the script reuses those resolved biographies before hitting live Wikipedia. That improves stability inside this repository but should be disclosed in replication notes.
- Because the unified database has no district/judge variables, this output should be treated as a reproducible derived layer built on top of the structured database, not as native database fields.
