# Public-Defendant Process-Failure Memo

Provisional note-facing memo based only on already-generated overnight outputs and the existing unified database while the disability-wave OpenRouter run continues.

## Bottom line

The current overnight record already supports a bounded but strong claim: disability FHA cases against public and quasi-public defendants appear to fail less because plaintiffs lack any grievance at all, and more because these disputes are routed through process-heavy, authority-fragmented, documentation-dependent decision environments that especially punish pro se and individual claimants.

That is a useful note-facing finding now, even before the new autopsy layer returns.

## What this memo uses

- `results/unified_overnight_public_process_report.md`
- `results/unified_follow_on_opportunities.md`
- `results/unified_overnight_raw_text_exemplar_packet.md`
- `/mnt/c/Users/nickg/OneDrive/Documents/Note/results/unified_overnight_current-data-opportunities.md`
- `/mnt/c/Users/nickg/OneDrive/Documents/Note/data/2/unified_raw_text_target_inventory.json`
- `/mnt/c/Users/nickg/OneDrive/Documents/Note/data/2/FHA_Unified_Database.json`
- `results/unified_overnight_tractability_report.md`
- `results/MEMO_H7_H1_H2_FINDINGS.md`

## Current evidence

### 1. The subset is real and usable now

- The raw-text inventory identifies `413` public-defendant process cases in the screened corpus.
- `250` are already exported into the working queue.
- `33` exported cases already have resolvable raw text.
- The bucket is dominated by `HOUSING_AUTHORITY` defendants, exactly the defendant type the follow-on memo flagged as most important.

### 2. Public-side process cases already look harder than private-side process cases

From the current public-process report:

- Public/quasi-public process-oriented cases: `520`; decided `461`; broad plaintiff win rate `28.4%`.
- Private process-oriented cases: `839`; decided `687`; broad plaintiff win rate `35.8%`.

So the public-side process docket is already about `7.4` percentage points worse on a broad-win measure, before any refined mechanism coding arrives.

### 3. The exported queue is mostly accommodation cases, and mostly early-stage losses

Within the exported `250` public-defendant process cases:

- Defendant types: `116` housing-authority, `110` municipality, `24` government.
- Primary claim type: `188` reasonable-accommodation-denial.
- Procedural posture: `102` motion to dismiss, `45` summary judgment, `45` appeal, `30` other procedural.
- Outcomes: `149` defendant wins, `35` procedural dispositions, `34` plaintiff wins, `30` mixed, `2` settlements.

This is not mainly a merits-trial bucket. It is a process bucket in the literal sense: the disputes are disproportionately being decided at pleading, threshold, or record-review stages.

### 4. Pro se status sharply worsens the public-process subset

Within the same exported queue:

- Pro se cases: `114`; represented cases: `136`.
- Decided pro se broad-win rate: `18.6%`.
- Decided represented broad-win rate: `39.7%`.
- At the motion-to-dismiss stage, pro se broad-win rate is only `12.7%` (`8/63`) versus `42.4%` (`14/33`) for represented plaintiffs.

That result fits the broader overnight story: public-defendant process cases are not just hard; they are especially hard when the plaintiff has to translate an accommodation problem into a legally adequate, defendant-specific process claim without institutional help.

### 5. Courts do somewhat better when the process is concrete and documented

Two current outputs point in the same direction.

First, in the exported public-process queue, cases marked as discussing an interactive process do modestly better than the rest:

- Interactive-process discussed: `61` cases; decided broad-win rate `36.8%`.
- No interactive-process discussion: `189` cases; decided broad-win rate `27.6%`.

Second, the tractability memo reports that measurable/documentable proxy cases outperform the rest of the docket:

- Measurable/documentable proxy cases: `495`; decided `421`; broad win `39.9%`.
- Other cases: `2027`; decided `1602`; broad win `28.1%`.

The implication is not that documentation guarantees victory. It is that courts are more receptive when the dispute is reduced to identifiable requests, dates, notices, denials, inspections, records, and decision points.

## Most plausible process-failure mechanisms

The current evidence supports four main mechanisms, plus one narrower auxiliary mechanism.

### Mechanism 1. Request-articulation and pleading failure

This is the most plausible front-end failure mode, especially in housing-authority and voucher cases.

The pattern appears in cases like:

- `Logan v. Matveevskii` (housing authority; pro se; defendant win; motion to dismiss), where the claim turned on an attempted transfer/accommodation theory but failed at the pleading stage.
- `Margaret Kris v. Dusseault Family Revocable Trust` / `Kris v. Dusseault Family Revocable Trust of 2017` (housing-authority-linked Section 8 setting; pro se; defendant win), where the plaintiff tried to convert housing and transfer difficulties into accommodation claims but could not plausibly connect the authority defendant, the request, and the requested relief.

The broader overnight numbers reinforce that reading. Public-process cases are mostly accommodation cases, mostly early-stage cases, and pro se plaintiffs perform dramatically worse at MTD. That combination strongly suggests that many losses occur before courts ever reach a full merits evaluation of whether an accommodation should have been granted.

### Mechanism 2. Eligibility, necessity, and documentation burdens

A second recurring mechanism is not pure pleading failure but process failure through proof burdens: courts demand concrete documentation showing disability-related necessity, equal-opportunity effects, program eligibility, or feasibility.

Examples in the current queue include:

- `DeCambre v. Brookline Housing Authority`, where the dispute centered on income calculation and program administration in a Section 8 setting.
- `Palm Partners, LLC v. City of Oakland Park`, where the operator lost in a zoning/accommodation dispute after the city process and the requested exception were evaluated through a record-heavy, feasibility-focused lens.
- `Cynthia Madej v. Jeff Maiden`, where plaintiffs could not convert a disability-linked environmental concern into a successful accommodation claim against a public official.
- `Sailboat Bend Sober Living v. City of Fort Lauderdale`, where the accommodation theory failed against fire-code and zoning requirements.

This mechanism matters for the note because it shows that public-defendant loss is not limited to obvious no-request cases. Even when a request exists, plaintiffs often still lose unless they can document necessity in a way the court recognizes as administratively legible.

### Mechanism 3. Institutional-authority fragmentation

This is the most note-relevant public-defendant mechanism.

In many public cases, the practical decisionmaker, the legally responsible defendant, and the record-holding institution are not cleanly aligned. Housing authorities, municipal departments, contractors, inspectors, hearing officers, and federal agencies all appear in the queue. That creates a repeat problem: the plaintiff experiences one housing process, but the litigation has to identify the exact actor with legal authority over the challenged decision.

Examples:

- `Arthur v. District of Columbia Housing Authority` survives only in part, with timeliness and defendant-specific issues shrinking the case even though an accommodation problem was clearly alleged.
- `Nat'l Fair Hous. Alliance v. Carson` shows a government-process dispute collapsing into threshold administrative-law barriers rather than merits resolution of the housing-governance problem.
- The Kris cases also fit this pattern because the plaintiff's housing problem crossed landlord, voucher, and authority lines in a way that made defendant linkage difficult.

This mechanism is especially important because it is distinctively public. Private-landlord accommodation cases can be hard, but public and quasi-public systems multiply the number of handoffs, records, and authority splits a plaintiff has to navigate.

### Mechanism 4. Neutral-rule and code-enforcement override

Municipal defendants often win by reframing the dispute as ordinary enforcement of a neutral zoning, fire-safety, occupancy, or permitting rule, with the accommodation request treated as too broad, unnecessary, or structurally incompatible with the scheme.

Examples:

- `Summers v. City of Fitchburg` (sprinkler-law enforcement; defendant win).
- `Palm Partners` (conditional-use and zoning framework; defendant win).
- `Sailboat Bend` (zoning and fire-code framework; defendant win).
- `Holy Ghost Revival Ministries v. City of Marysville` (zoning-enforcement posture; pleading-stage loss).

The important counterexamples are just as revealing:

- `Oxford House, Inc. v. Browning` (plaintiff win).
- `Anderson v. City of Blue Ash` (mixed/plaintiff-favorable appellate result).

Those cases suggest plaintiffs do better when they can translate the dispute into a tightly framed conflict between a specific disability-related need and a specific public rule, rather than attacking the entire regulatory structure at a high level of abstraction.

### Mechanism 5. Delay and navigation failure, but only when concretized

Delay does appear in the current queue, but it does not look like the dominant stand-alone mechanism. It looks more like a secondary problem that matters only when paired with a concrete request trail.

Examples:

- `Arthur` involves delay plus a clearly alleged accommodation problem and survives in part.
- `Wright v. Mishawaka Housing Authority` also survived in part where the housing authority's actions and the plaintiff's need were concretely described.
- By contrast, many delay-inflected voucher and housing-authority cases still lose where the record does not cleanly tie the delay to a definite accommodation duty.

So the better framing is not simply "public defendants delay." It is: delay becomes legally meaningful only when the plaintiff can show a documented request, a responsible official, and a decision trail.

## Synthesis

Taken together, the current record suggests that public-defendant disability cases fail through a stacked process burden:

1. the plaintiff must formulate a legally legible request;
2. connect that request to disability-related necessity;
3. identify the institution or official with actual authority;
4. show a documented denial, delay, or refusal;
5. overcome the defendant's reframing of the dispute as ordinary program administration or neutral code enforcement.

That stack is difficult for any plaintiff, but especially punishing for pro se tenants, voucher holders, and other individual claimants with fragmented paper trails. The current numbers strongly suggest that this is a structural problem in the public-process subset, not a handful-of-bad-cases anecdote.

## What this implies for Tier 1 and Tier 2

### Tier 1

Tier 1 should emphasize facts that are concrete, duty-anchored, and already familiar to courts in the better-performing tractable cases:

- whether a request was actually made;
- when it was made;
- to whom it was made;
- what documentation was supplied;
- what authority that official had;
- what written response, denial, or delay followed.

That fits the tractability result: measurable/documentable cases materially outperform the rest of the docket. Tier 1 should therefore be framed not as broad integration planning, but as collection and disclosure of request logs, transfer/voucher records, inspection and code-enforcement records, and written accommodation decisions.

### Tier 2

Tier 2 should target the specifically public failure points that Tier 1 alone will not solve:

- cross-agency authority mapping;
- written identification of the official or office with final accommodation authority;
- timeline auditing for request receipt, response, escalation, and closure;
- reason-giving requirements when a public entity invokes safety, zoning, or program-administration rationales;
- record-linkage rules for voucher administrators, housing authorities, contractors, and municipal enforcement bodies.

In note terms, Tier 2 is where the model responds directly to public-defendant fragmentation. It converts "someone in government handled this badly" into verifiable institutional duties tied to actual decision points.

## What this implies for the note

The current evidence supports a note-facing claim narrower and stronger than a generic accusation of public hostility.

The better claim is:

- disability FHA cases against public defendants are especially vulnerable to process collapse;
- that collapse usually occurs through pleading failure, documentation failure, authority fragmentation, and neutral-rule override rather than overt merits rejection alone;
- plaintiffs do better when the dispute is translated into specific, documentable, duty-linked facts;
- that is precisely why a reinforcement model built around Tier 1 and Tier 2 makes sense.

So this memo supports using the public-defendant subset as an institutional bridge in the note: it shows why disability-centered AFFH reform should reinforce concrete, reviewable public duties instead of relying on open-textured governance aspirations alone.

## Immediate note-facing takeaway

Even without the new autopsy layer, the overnight outputs already justify a bounded thesis: the public-defendant disability docket looks like a governance-and-process failure domain. The strongest response is not broader abstraction. It is more specific, more documentable, and more authority-specific obligations of the kind Tier 1 and Tier 2 are designed to impose.
