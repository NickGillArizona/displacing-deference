# Unified Overnight Autopsy Analysis

Generated: 2026-04-15T06:30:17Z
Status: fallback_only

## Input coverage

- Screened cases analyzed: 2522
- Overnight result rows present: 0
- Cases using overnight labels: 0
- Cases using fallback heuristics: 2522
- Citation baseline present: True
- Raw-text inventory present: True

## Pleading failure family distribution

| Family | Cases |
|---|---:|
| NO_FAILURE_PLAINTIFF_WIN | 618 |
| CAUSAL_LINK | 420 |
| TRANSLATION | 393 |
| UNCLEAR | 365 |
| MERITS_EVIDENCE | 359 |
| NO_FAILURE_DEFENDANT_WIN | 180 |
| FACTUAL_DETAIL | 94 |
| PROCEDURAL_GATEWAY | 93 |

## Pleading mechanism distribution

| Mechanism | Cases |
|---|---:|
| CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS | 618 |
| ADVERSE_ACTION_NOT_CONNECTED | 469 |
| ELEMENTS_NOT_TIED_TO_FACTS | 389 |
| UNCLEAR | 365 |
| REQUEST_NOT_ALLEGED | 206 |
| INTERACTIVE_PROCESS_BREAKDOWN | 188 |
| DISABILITY_NEXUS_MISSING | 91 |
| STATUTORY_HOOK_UNCLEAR | 59 |
| LIMITATIONS_OR_TIMELINESS | 48 |
| JURISDICTION_OR_STANDING | 45 |
| POLICY_OR_PRACTICE_NOT_SPECIFIED | 24 |
| TECHNICAL_PROOF_GAP | 20 |

## Confidence / review queue status

| Confidence | Cases |
|---|---:|
| MEDIUM | 1694 |
| HIGH | 758 |
| LOW | 70 |

| Raw-text review priority | Cases |
|---|---:|
| MEDIUM | 1317 |
| LOW | 693 |
| HIGH | 512 |

## Key subgroup counts

- Pro se cases: 1391
- Represented cases: 1129
- Public-process flagged cases: 352
- High doctrinal-gap cases: 259
- High raw-text-priority cases: 512
- Low-confidence cases: 70
- Core institutional-missing queue (theory/fact development): 1231

## Pro se family distribution

| Family | Cases |
|---|---:|
| CAUSAL_LINK | 373 |
| TRANSLATION | 333 |
| UNCLEAR | 195 |
| NO_FAILURE_PLAINTIFF_WIN | 153 |
| NO_FAILURE_DEFENDANT_WIN | 105 |
| MERITS_EVIDENCE | 103 |
| FACTUAL_DETAIL | 70 |
| PROCEDURAL_GATEWAY | 59 |

## Represented family distribution

| Family | Cases |
|---|---:|
| NO_FAILURE_PLAINTIFF_WIN | 465 |
| MERITS_EVIDENCE | 256 |
| UNCLEAR | 169 |
| NO_FAILURE_DEFENDANT_WIN | 75 |
| TRANSLATION | 60 |
| CAUSAL_LINK | 46 |
| PROCEDURAL_GATEWAY | 34 |
| FACTUAL_DETAIL | 24 |

## Public-process family distribution

| Family | Cases |
|---|---:|
| TRANSLATION | 144 |
| NO_FAILURE_PLAINTIFF_WIN | 68 |
| MERITS_EVIDENCE | 63 |
| UNCLEAR | 37 |
| NO_FAILURE_DEFENDANT_WIN | 25 |
| PROCEDURAL_GATEWAY | 15 |

## Immediate queues

- Top high-priority raw-text queue exported in JSON: 25 records.
- Top public-process queue exported in JSON: 25 records.
- Top doctrinal-gap queue exported in JSON: 25 records.

## Notes

- This file is the infrastructure layer for the overnight pleading-autopsy lane rather than a polished substantive memo.
- When `unified_overnight_results.json` is absent or incomplete, the script uses conservative structured-data fallback classifications and marks that coverage explicitly.
- Detailed merged case-level output is in `/mnt/c/Users/nickg/OneDrive/Documents/Note/data/2/unified_overnight_autopsy_analysis.json`.
