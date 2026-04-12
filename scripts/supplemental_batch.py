"""
Supplemental Classification Batch: H1 (Claim Specificity) + H2 (Technical Complexity)

Classifies all screened-in FHA cases on:
  - claim_specificity (SPECIFIC_DUTY / MIXED / OPEN_TEXTURED)
  - technical_complexity (LOW / MODERATE / HIGH)
  - enacted_duty_flag, measurable_facts_flag, expert_proof_needed,
    multi_defendant, physical_evidence_present, public_quasi_public_defendant

Uses existing extracted data as input (not raw opinion text) for efficiency.

Usage:
  python supplemental_batch.py submit     # Submit batch
  python supplemental_batch.py status     # Check status
  python supplemental_batch.py download   # Download results
"""
import json
import os
import sys
import hashlib
import anthropic

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-haiku-4-5"
TEMPERATURE = 0.0
MAX_TOKENS = 1024

DB_PATH = 'C:/Users/nickg/OneDrive/Documents/Note/data/2/FHA_Unified_Database.json'
OUTPUT_PATH = 'C:/Users/nickg/OneDrive/Documents/Note/supplemental_classification_results.json'
BATCH_ID_FILE = 'C:/Users/nickg/OneDrive/Documents/Note/supplemental_batch_id.txt'
ID_LOOKUP_FILE = 'C:/Users/nickg/OneDrive/Documents/Note/supplemental_id_lookup.json'
ERROR_LOG = 'C:/Users/nickg/OneDrive/Documents/Note/supplemental_batch_errors.json'

SYSTEM_PROMPT = """You are a legal research assistant performing supplemental classification of federal court FHA opinions. You receive previously extracted structured case data and classify additional dimensions.

Return ONLY valid JSON matching the output schema. No commentary or explanation."""

USER_PROMPT_TEMPLATE = """Classify this FHA case on claim specificity and technical complexity based on the extracted data below.

CASE DATA:
{case_data}

OUTPUT SCHEMA:
{{
  "claim_specificity": "SPECIFIC_DUTY | MIXED | OPEN_TEXTURED",
  "specificity_reasoning": "1-2 sentences",
  "enacted_duty_flag": true/false,
  "measurable_facts_flag": true/false,
  "technical_complexity": "LOW | MODERATE | HIGH",
  "complexity_reasoning": "1-2 sentences",
  "expert_proof_needed": true/false,
  "multi_defendant": true/false,
  "physical_evidence_present": true/false,
  "public_quasi_public_defendant": true/false
}}

CLASSIFICATION RULES:

CLAIM SPECIFICITY — classifies the nature of the legal duty at issue:

SPECIFIC_DUTY: The case's FHA claims are anchored to discrete, enacted statutory provisions with identifiable compliance criteria. The court's analysis turns on whether the defendant satisfied or violated a specific statutory or regulatory requirement.
Indicators:
- Claims under section 3604(f)(3)(B) (reasonable accommodation) with a specific, identified accommodation request that was denied or mishandled
- Claims under section 3604(f)(3)(C) (design and construction) with specific accessibility standards at issue
- Claims under section 3604(f)(1) (discriminatory refusal or terms) with an identified adverse action tied to disability
- Retaliation claims under section 3617 with a specific protected activity and adverse action
- The court applies a specific legal test (necessity + reasonableness for RA, intent for disparate treatment, prima facie elements)
- The dispute centers on whether a particular statutory duty was met, not on broad policy

OPEN_TEXTURED: The case's claims rely on broad statutory purpose, generalized policy goals, or open-ended planning duties without specific compliance criteria.
Indicators:
- Claims framed as failure to affirmatively further fair housing under section 3608(d)
- Generalized pattern-or-practice allegations without specific statutory hooks
- The court discusses broad policy goals, integration objectives, or community-level impact rather than specific violations
- Vague discrimination allegations without clear statutory basis or identified adverse action
- Claims that require the court to assess policy choices, resource allocation, or systemic practices rather than compliance with a discrete rule

MIXED: The case contains both specific-duty and open-textured claims, or a single claim that blends specific statutory elements with broader policy framing.

ENACTED DUTY FLAG: True if the court's analysis is grounded in compliance with a specific, enacted statutory or regulatory duty (section 3604(f)(3)(B) accommodation requirement, section 3604(f)(3)(C) design standards, specific HUD regulation, section 3617 anti-retaliation). False if the court's analysis is grounded in broader purpose-driven interpretation or policy assessment.

MEASURABLE FACTS FLAG: True if the court's reasoning relies on documentable, measurable, or objectively verifiable facts: physical measurements, medical documentation, denial letters, accommodation request records, specific dates and communications, policies with clear terms. False if the reasoning primarily addresses intent, motive, generalized discrimination patterns, or policy adequacy.

TECHNICAL COMPLEXITY:

LOW: Straightforward factual predicate. Single defendant. Clear documentation available. No expert or specialized proof needed.
Examples: ESA denial where landlord refused a documented request; straightforward refusal to rent based on known disability; simple failure to respond to accommodation request with clear paper trail.

MODERATE: Multiple factual predicates or procedural steps. Interactive process analysis across multiple communications. Multiple accommodation requests. Comparative evidence needed. Some document assembly required.
Examples: Failure to engage in interactive process with back-and-forth communications; discriminatory terms requiring comparison to non-disabled tenants; reasonable accommodation dispute with competing evidence on burden or necessity.

HIGH: Requires expert testimony, technical measurements, architectural analysis, statistical evidence, or specialized professional knowledge. Complex entity relationships or multiple defendants. Regulatory compliance analysis requiring specialized expertise. Design and construction standard compliance.
Examples: Design and construction violations requiring measurement against FHAG standards; structural modifications requiring engineering assessment; pattern-or-practice claims requiring statistical analysis; multi-defendant cases with complex allocation of responsibility; subsidy program compliance disputes requiring HUD regulatory expertise.

EXPERT PROOF NEEDED: True if resolving the case on the merits requires or would substantially benefit from expert testimony, technical measurements, architectural analysis, statistical evidence, or specialized professional assessment. False for cases resolvable on documentary evidence and lay testimony alone.

MULTI DEFENDANT: True if the case names more than one distinct defendant entity. Ignore Doe defendants or fictitious parties. Count based on the case data provided.

PHYSICAL EVIDENCE PRESENT: True if the case involves or references physical evidence: photographs, measurements, inspection reports, blueprints, site surveys, physical property characteristics, accessibility features. False if the case is resolved entirely on documentary and testimonial evidence about communications, policies, or decisions.

PUBLIC/QUASI-PUBLIC DEFENDANT: True if any defendant is a public housing authority, municipality, government entity, or quasi-public entity (subsidized housing provider, entity receiving direct government funding for housing). Also true if housing_type indicates public or subsidized housing (PUBLIC_HOUSING, SECTION_8, LIHTC, SECTION_811, SECTION_202). False if all defendants are purely private market actors."""


def extract_case_fields(record):
    """Extract the relevant fields from a Unified DB record for classification."""
    fields = {
        'case_name': record.get('case_name', ''),
        'year': record.get('year'),
        'court': record.get('court', ''),
        'procedural_posture': record.get('procedural_posture', ''),
        'fha_section_cited': record.get('fha_section_cited', ''),
        'accommodation_type': record.get('accommodation_type', ''),
        'plaintiff_type': record.get('plaintiff_type', ''),
        'defendant_type': record.get('defendant_type', ''),
        'disability_category': record.get('disability_category', ''),
        'outcome': record.get('outcome', ''),
        'claim_types': record.get('claim_types', []),
        'interactive_process_discussed': record.get('interactive_process_discussed', ''),
        'housing_type': record.get('housing_type', ''),
        'accommodation_description': record.get('accommodation_description', ''),
        'key_holding': record.get('key_holding', ''),
        'brief_summary': record.get('brief_summary', ''),
        'pro_se': record.get('pro_se', False),
    }
    # Include per-claim data (compact form)
    claims = []
    for c in record.get('fha_claims', []):
        claims.append({
            'theory': c.get('theory', ''),
            'accommodation_type': c.get('accommodation_type', ''),
            'stage': c.get('stage', ''),
            'dismissal_reason': c.get('dismissal_reason', ''),
            'outcome': c.get('outcome', ''),
            'reasoning': c.get('reasoning', ''),
        })
    fields['fha_claims'] = claims
    return fields


def make_safe_id(source_file, index):
    h = hashlib.md5(source_file.encode()).hexdigest()[:12]
    return f"supp-{index:04d}-{h}"


def build_requests():
    with open(DB_PATH, encoding='utf-8') as f:
        db = json.load(f)

    # Filter to screened-in cases
    screened = [r for r in db if r.get('screening_result') == 'YES']
    print(f"Total records: {len(db)}")
    print(f"Screened-in: {len(screened)}")

    requests = []
    id_lookup = {}

    for index, record in enumerate(screened):
        sf = record.get('source_file', f'record_{index}')
        case_fields = extract_case_fields(record)
        case_data_json = json.dumps(case_fields, indent=2, ensure_ascii=False)
        user_prompt = USER_PROMPT_TEMPLATE.format(case_data=case_data_json)

        safe_id = make_safe_id(sf, index)
        id_lookup[safe_id] = sf

        requests.append({
            "custom_id": safe_id,
            "params": {
                "model": MODEL,
                "max_tokens": MAX_TOKENS,
                "temperature": TEMPERATURE,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": user_prompt}],
            }
        })

    with open(ID_LOOKUP_FILE, 'w', encoding='utf-8') as f:
        json.dump(id_lookup, f, indent=2)

    print(f"Built {len(requests)} requests")
    print(f"ID lookup saved to {ID_LOOKUP_FILE}")
    return requests


def submit_batch():
    client = anthropic.Anthropic(api_key=API_KEY)
    requests = build_requests()

    print(f"\nSubmitting single batch of {len(requests)} requests...")
    batch = client.messages.batches.create(requests=requests)

    with open(BATCH_ID_FILE, 'w') as f:
        f.write(batch.id)

    print(f"Batch ID: {batch.id}")
    print(f"Status: {batch.processing_status}")

    # Estimate cost
    # ~1500 tokens avg input per case, ~300 tokens output
    est_input = len(requests) * 1500 / 1e6
    est_output = len(requests) * 300 / 1e6
    est_cost = est_input * 0.40 + est_output * 2.00
    print(f"\nEstimated cost: ~${est_cost:.2f} (batch pricing)")
    print(f"Check status:  python supplemental_batch.py status")
    print(f"Download:      python supplemental_batch.py download")


def check_status():
    client = anthropic.Anthropic(api_key=API_KEY)
    if not os.path.exists(BATCH_ID_FILE):
        print("No batch ID found. Run 'submit' first.")
        return False

    with open(BATCH_ID_FILE) as f:
        batch_id = f.read().strip()

    batch = client.messages.batches.retrieve(batch_id)
    counts = batch.request_counts
    total = counts.processing + counts.succeeded + counts.errored + counts.canceled + counts.expired

    print(f"Batch: {batch_id}")
    print(f"Status: {batch.processing_status}")
    print(f"Succeeded: {counts.succeeded}/{total}")
    print(f"Processing: {counts.processing}")
    print(f"Errored: {counts.errored}")

    return batch.processing_status == "ended"


def download_results():
    client = anthropic.Anthropic(api_key=API_KEY)
    if not os.path.exists(BATCH_ID_FILE):
        print("No batch ID found. Run 'submit' first.")
        return

    with open(BATCH_ID_FILE) as f:
        batch_id = f.read().strip()

    batch = client.messages.batches.retrieve(batch_id)
    if batch.processing_status != "ended":
        print(f"Batch not complete. Status: {batch.processing_status}")
        print(f"Succeeded: {batch.request_counts.succeeded}, Processing: {batch.request_counts.processing}")
        return

    if os.path.exists(ID_LOOKUP_FILE):
        with open(ID_LOOKUP_FILE, encoding='utf-8') as f:
            id_lookup = json.load(f)
    else:
        id_lookup = {}

    print(f"Downloading results for batch {batch_id}...")

    results = []
    errors = []
    total_input_tokens = 0
    total_output_tokens = 0

    for result in client.messages.batches.results(batch_id):
        sf = id_lookup.get(result.custom_id, result.custom_id)

        if result.result.type == "succeeded":
            message = result.result.message
            raw = message.content[0].text
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens

            try:
                text = raw.strip()
                if text.startswith('```'):
                    text = text.split('\n', 1)[1] if '\n' in text else text[3:]
                if text.endswith('```'):
                    text = text[:-3].rstrip()

                parsed = json.loads(text)
                results.append({
                    'source_file': sf,
                    'custom_id': result.custom_id,
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'classification': parsed,
                })
            except json.JSONDecodeError as e:
                errors.append({
                    'source_file': sf,
                    'error': f'JSON parse: {str(e)}',
                    'raw': raw[:2000],
                })
        else:
            errors.append({
                'source_file': sf,
                'error': f'Result type: {result.result.type}',
            })

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    if errors:
        with open(ERROR_LOG, 'w', encoding='utf-8') as f:
            json.dump(errors, f, indent=2, ensure_ascii=False)

    cost = total_input_tokens / 1e6 * 0.40 + total_output_tokens / 1e6 * 2.00

    print(f"\n{'='*70}")
    print(f"DOWNLOAD COMPLETE")
    print(f"{'='*70}")
    print(f"Succeeded: {len(results)}")
    print(f"Errors: {len(errors)}")
    print(f"Tokens: {total_input_tokens:,} input + {total_output_tokens:,} output")
    print(f"Cost: ${cost:.2f} (batch pricing)")
    print(f"Output: {OUTPUT_PATH}")
    if errors:
        print(f"Error log: {ERROR_LOG}")

    # Quick distribution check
    specs = [r['classification'].get('claim_specificity', 'MISSING') for r in results]
    comps = [r['classification'].get('technical_complexity', 'MISSING') for r in results]
    from collections import Counter
    print(f"\nClaim specificity distribution:")
    for k, v in Counter(specs).most_common():
        print(f"  {k}: {v} ({v/len(results)*100:.1f}%)")
    print(f"\nTechnical complexity distribution:")
    for k, v in Counter(comps).most_common():
        print(f"  {k}: {v} ({v/len(results)*100:.1f}%)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python supplemental_batch.py submit    # Submit batch")
        print("  python supplemental_batch.py status    # Check status")
        print("  python supplemental_batch.py download  # Download results")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == 'submit':
        submit_batch()
    elif cmd == 'status':
        check_status()
    elif cmd == 'download':
        download_results()
    else:
        print(f"Unknown: {cmd}. Use submit/status/download.")
