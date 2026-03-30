## Appendix C: *Iqbal* Citation Analysis

### C.1 Overall *Iqbal* Effect (FHA Pilot Database, n=331)

| *Iqbal* Cited | n | Defendant Win | D-Win Rate |
|---------------|---|--------------|------------|
| Yes | 34 | 23 | 67.6% |
| No | 297 | 120 | 40.4% |

**Chi-squared test:** p = 0.0014

### C.2 *Iqbal* Effect at Motion-to-Dismiss Stage (n=86 MTD cases)

| *Iqbal* Cited at MTD | n | Defendant Win | D-Win Rate |
|-----------------------|---|--------------|------------|
| Yes | 21 | 14 | 66.7% |
| No | 65 | 28 | 43.1% |

**Chi-squared test:** p = 0.032

### C.3 Cross-Class Citation Disparity

Disability-based MTD cases cite *Iqbal* at **3.3 times** the rate of race-based MTD cases (39.5% vs. 12.0%; disability MTD n=38, race MTD n=25).

**Caveat:** Citation patterns may reflect case characteristics rather than judicial bias. Courts may cite *Iqbal* more frequently when claims are less well-pleaded. The disparity finding is descriptive and does not establish that *Iqbal* is being applied more stringently to disability claims as a matter of doctrine.

### C.4 RA Database Corroboration (n=1,857)

#### C.4.1 Detection Methodology

The RA Database does not contain a dedicated *Iqbal* citation field. Citations were detected by searching the `key_cases_cited` field for any element matching the case-insensitive pattern `iqbal`. This approach differs from the FHA Pilot Database's manual coding: `key_cases_cited` captures citations the classification models identified as significant to the opinion, not every citation in the text.

*Twombly* was detected using the same methodology. Of the 723 *Iqbal*-citing records, 626 (86.6%) also cited *Twombly*; of the 695 *Twombly*-citing records, 626 (90.1%) also cited *Iqbal*.

#### C.4.2 Overall *Iqbal* Effect (RA Database, n=1,857)

| *Iqbal* Cited | n | DW | DW% | PW | MIXED | PW Strict | PW Broad |
|---------------|-----|-----|------|-----|-------|-----------|----------|
| Yes | 723 | 514 | 71.1% | 53 | 101 | 7.3% | 21.3% |
| No | 1,134 | 539 | 47.5% | 130 | 80 | 11.5% | 19.2% |

| Test | Chi-squared | p-value |
|------|-------------|---------|
| Defendant win rate | 99.84 | <0.0001 |
| Strict plaintiff win rate | 8.49 | 0.0036 |
| Broad plaintiff win rate | 1.18 | 0.28 (not significant) |

The defendant win rate is 23.6 percentage points higher when *Iqbal* is cited. However, the broad plaintiff win rate is *not* significantly different (21.3% vs. 19.2%, p=0.28), reflecting the substantially higher MIXED outcome rate in *Iqbal*-cited cases (14.0% vs. 7.1%).

#### C.4.3 *Iqbal* at Motion to Dismiss (RA Database, n=946)

| *Iqbal* at MTD | n | DW | DW% | PW | MIXED | PW Strict | PW Broad |
|----------------|-----|-----|------|-----|-------|-----------|----------|
| Yes | 645 | 473 | 73.3% | 50 | 92 | 7.8% | 22.0% |
| No | 301 | 202 | 67.1% | 27 | 22 | 9.0% | 16.3% |

At MTD, the broad rate pattern *reverses*: *Iqbal*-cited MTD cases have a *higher* broad rate (22.0% vs. 16.3%, p=0.043), confirming that *Iqbal* citation at the pleading stage is associated with more partial motion survival (MIXED outcomes).

#### C.4.4 Temporal Patterns

*Iqbal* citation rates were stable across the study period. Pre-*Loper Bright* rate: 38.4% (360/938); post-*Loper Bright*: 39.5% (363/919). However, outcomes conditional on *Iqbal* citation deteriorated post-*Loper Bright*:

| MTD + *Iqbal* Cited | n | DW% | PW Strict | PW Broad |
|---------------------|-----|------|-----------|----------|
| Pre-LB | 320 | 67.5% | 10.3% | 26.6% |
| Post-LB | 325 | 79.1% | 5.2% | 17.5% |

Post-*Loper Bright* defendant win rates at MTD rose by 11.6 percentage points in *Iqbal*-cited cases and 8.4 points in non-*Iqbal* cases, suggesting that the post-*Loper Bright* deterioration operates through mechanisms beyond *Iqbal* pleading standards.

#### C.4.5 Reconciling the Two Databases

| Feature | FHA Pilot Database | RA Database |
|---------|-------------------|-------------|
| **Sample** | 331 cases, all protected classes | 1,857 cases, all protected classes (59.1% disability) |
| **Period** | 2012–2026 | 2021–2026 |
| **Detection** | Manual coding of *Iqbal* citation presence | Automated extraction via `key_cases_cited` field |
| **Key finding** | Cross-class disparity: disability cites *Iqbal* 3.3x race rate | Within-disability effect: higher DW, higher MIXED, lower strict PW |
| **Limitation** | Small n at MTD (n=86) | No cross-class comparison possible |

---
