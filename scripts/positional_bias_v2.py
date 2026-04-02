"""
Positional Bias Analysis v2
Instead of a fixed keyword map, extract key phrases from each model's
accommodation_description and search for those in the full opinion text.
This catches case-specific language the fixed map misses.
"""
import json, re, os
from collections import Counter
from config import DB_RA_RESOLVED_PATH, CASE_DIR, RESULTS_DIR

with open(DB_RA_RESOLVED_PATH, encoding='utf-8') as f:
    resolved = json.load(f)

# ---- Broader keyword map (v2) ----
# Each category gets both specific terms AND general terms that appear in opinions
CATEGORY_KEYWORDS = {
    'ASSISTANCE_ANIMAL': [
        'assistance animal', 'emotional support animal', 'esa',
        'service animal', 'service dog', 'companion animal', 'support animal',
        'no-pet', 'no pet', 'pet policy', 'pet deposit', 'animal policy',
        'therapy dog', 'therapy animal', 'comfort animal',
        'pet restriction', 'animal restriction', 'dog policy',
    ],
    'PARKING': [
        'parking', 'designated spot', 'handicap space', 'reserved space',
        'accessible parking', 'parking space', 'parking lot', 'parking spot',
        'handicapped parking', 'disabled parking',
    ],
    'STRUCTURAL_MODIFICATION': [
        'ramp', 'grab bar', 'wheelchair', 'widened door', 'roll-in shower',
        'handrail', 'structural modification', 'physical modification',
        'railing', 'accessibility modification', 'bathroom modification',
        'door widening', 'threshold', 'accessible shower', 'stair lift',
        'chairlift', 'lowered counter', 'accessible route',
        'handicap ramp', 'wheelchair ramp', 'accessibility feature',
    ],
    'TRANSFER': [
        'unit transfer', 'transfer to', 'relocat', 'different unit',
        'move to another', 'accessible unit', 'ground floor',
        'first floor unit', 'ground-floor', 'lower floor',
        'unit reassignment', 'alternate unit',
    ],
    'EVICTION_DEFENSE': [
        'eviction', 'evict', 'lease termination', 'notice to quit',
        'second chance', 'cure period', 'unlawful detainer',
        'termination of tenancy', 'notice to vacate', 'lease violation',
        'tenancy termination', 'nonrenewal', 'non-renewal',
    ],
    'LIVE_IN_AIDE': [
        'live-in aide', 'live in aide', 'caregiver', 'additional occupant',
        'personal care attendant', 'home health aide', 'live-in caretaker',
        'in-home aide', 'occupancy limit', 'extra occupant',
    ],
    'SOBER_LIVING_GROUP_HOME_ZONING': [
        'sober living', 'group home', 'recovery home', 'halfway house',
        'zoning', 'oxford house', 'residential treatment', 'sober home',
        'recovery house', 'substance abuse', 'drug treatment',
        'alcohol treatment', 'group residence', 'community residence',
        'single family zoning', 'zoning ordinance', 'zoning restriction',
    ],
    'COMMUNICATION_ACCOMMODATION': [
        'large print', 'interpreter', 'written notice', 'braille',
        'communication accommodation', 'accessible format', 'tty',
        'relay service', 'sign language', 'hearing impaired',
        'visual impairment', 'blind', 'deaf', 'hearing aid',
        'accessible communication', 'alternative format',
        'communication barrier', 'language access',
    ],
    'RENT_PAYMENT': [
        'rent payment', 'payment plan', 'late fee', 'rent accommodation',
        'rental assistance', 'rent modification', 'payment modification',
        'rent subsidy', 'rent adjustment', 'housing voucher',
        'section 8', 'late rent', 'overdue rent', 'rent arrears',
    ],
    'POLICY_EXCEPTION': [
        'policy exception', 'waiver', 'exception to', 'modify policy',
        'rule exception', 'policy modification', 'reasonable modification',
        'exception to the rule', 'rule modification', 'policy change',
        'rule waiver', 'exemption', 'variance',
        'reasonable accommodation', 'accommodation request',
        'modification of policy', 'exception from',
    ],
    'DISCRIMINATION_PRIMARY': [
        'discriminat', 'disparate treatment', 'disparate impact',
        'intentional discrimination', 'fair housing act',
        'disability discrimination', 'handicap discrimination',
    ],
}


def scan_text(text):
    text_lower = text.lower()
    text_len = len(text_lower)
    if text_len == 0:
        return {}
    results = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        positions = []
        for kw in keywords:
            start = 0
            while True:
                idx = text_lower.find(kw, start)
                if idx == -1:
                    break
                positions.append(idx)
                start = idx + len(kw)
        if positions:
            positions.sort()
            # Remove duplicates from overlapping keywords
            positions = sorted(set(positions))
            best_density = 0
            for p in positions:
                ws = max(0, p - 500)
                we = min(text_len, p + 500)
                c = sum(1 for pp in positions if ws <= pp <= we)
                d = c / ((we - ws) / 1000) if we > ws else 0
                best_density = max(best_density, d)
            results[cat] = {
                'first_mention': positions[0],
                'first_mention_pct': round(positions[0] / text_len * 100, 1),
                'total_mentions': len(positions),
                'peak_density': round(best_density, 2),
            }
    return results


def desc_types(r):
    descs_parts = []
    for s in ['_minmax', '_deepseek', '_kimi', '']:
        d = r.get('accommodation_description' + s, '')
        if d:
            descs_parts.append(d)
    tl = ' '.join(descs_parts).lower()
    found = set()
    simple = {
        'ASSISTANCE_ANIMAL': ['animal', 'dog', 'esa', 'emotional support', 'service animal', 'pet'],
        'PARKING': ['parking'],
        'STRUCTURAL_MODIFICATION': ['ramp', 'grab bar', 'wheelchair', 'handrail'],
        'TRANSFER': ['transfer', 'relocat', 'different unit'],
        'EVICTION_DEFENSE': ['eviction', 'evict', 'lease termination'],
        'LIVE_IN_AIDE': ['live-in aide', 'caregiver', 'additional occupant'],
        'SOBER_LIVING': ['sober', 'group home', 'recovery', 'halfway house', 'zoning'],
        'COMMUNICATION': ['notice', 'large print', 'interpreter', 'blind', 'deaf'],
        'RENT_PAYMENT': ['rent', 'payment plan', 'late fee'],
        'POLICY_EXCEPTION': ['policy', 'waiver', 'exception', 'modification'],
    }
    for cat, kws in simple.items():
        for kw in kws:
            if kw in tl:
                found.add(cat)
                break
    return found


# ---- Identify ALL 38 target cases (different specific categories) ----
targets = []
for r in resolved:
    mm = r.get('accommodation_type_minmax', '').strip().upper()
    ds = r.get('accommodation_type_deepseek', '').strip().upper()
    ki = r.get('accommodation_type_kimi', '').strip().upper()
    residual = {'UNDETERMINED', 'OTHER', 'NONE', 'DISCRIMINATION_PRIMARY', ''}
    specific = [m for m in [mm, ds, ki] if m not in residual]
    if len(set(specific)) >= 2:
        targets.append(r)

print(f"Target cases (any 2+ different specific categories): {len(targets)}")

# CASE_DIR imported from config
results = []
skipped_no_file = 0
skipped_no_cats = 0

for tc in targets:
    sf = tc.get('source_file', '')
    txt_path = os.path.join(CASE_DIR, sf + '.txt')
    if not os.path.exists(txt_path):
        skipped_no_file += 1
        continue

    with open(txt_path, encoding='utf-8', errors='replace') as f:
        text = f.read()

    scan = scan_text(text)
    mm = tc.get('accommodation_type_minmax', '').strip().upper()
    ds = tc.get('accommodation_type_deepseek', '').strip().upper()
    ki = tc.get('accommodation_type_kimi', '').strip().upper()
    canon = tc.get('accommodation_type', '').strip().upper()

    # Which model-chosen categories can we find in the text?
    model_cats = set(m for m in [mm, ds, ki] if m in scan)
    if len(model_cats) < 2:
        skipped_no_cats += 1
        # Log what we missed
        all_model_vals = set(m for m in [mm, ds, ki] if m)
        missing = all_model_vals - set(scan.keys())
        continue

    first_mentioned = min(model_cats, key=lambda c: scan[c]['first_mention'])
    most_discussed = max(model_cats, key=lambda c: scan[c]['total_mentions'])
    # Tie-breaker for most_discussed: if tied on mentions, use density
    tied_max = [c for c in model_cats if scan[c]['total_mentions'] == scan[most_discussed]['total_mentions']]
    if len(tied_max) > 1:
        most_discussed = max(tied_max, key=lambda c: scan[c]['peak_density'])

    cr = {
        'case_name': tc.get('case_name', '')[:70],
        'source_file': sf,
        'outcome': tc.get('outcome', ''),
        'mm': mm, 'ds': ds, 'ki': ki, 'canon': canon,
        'first_mentioned_cat': first_mentioned,
        'most_discussed_cat': most_discussed,
        'same_first_and_most': first_mentioned == most_discussed,
        'text_length': len(text),
        'scan': {},
    }

    for cat in model_cats:
        s = scan[cat]
        cr['scan'][cat] = {
            'first_pos_pct': s['first_mention_pct'],
            'mentions': s['total_mentions'],
            'density': s['peak_density'],
        }

    for mn, mv in [('mm', mm), ('ds', ds), ('ki', ki)]:
        if mv not in model_cats:
            cr[mn + '_anchor'] = 'NOT_IN_TEXT'
        elif first_mentioned == most_discussed:
            cr[mn + '_anchor'] = 'BOTH_SAME' if mv == first_mentioned else 'OTHER_CAT'
        elif mv == first_mentioned:
            cr[mn + '_anchor'] = 'FIRST_MENTIONED'
        elif mv == most_discussed:
            cr[mn + '_anchor'] = 'MOST_DISCUSSED'
        else:
            cr[mn + '_anchor'] = 'OTHER_CAT'

    results.append(cr)

print(f"Scannable cases: {len(results)}")
print(f"Skipped (no file): {skipped_no_file}")
print(f"Skipped (< 2 cats in text): {skipped_no_cats}")
print(f"Cases where first != most: {sum(1 for r in results if not r['same_first_and_most'])}")

# ---- STEP 2: Correlation analysis ----
print("\n" + "=" * 70)
print("STEP 2: MODEL ANCHOR CORRELATION")
print("=" * 70)

# Only analyze cases where first != most (the informative ones)
informative = [r for r in results if not r['same_first_and_most']]
print(f"\nInformative cases (first != most): {len(informative)}")

for model in ['mm', 'ds', 'ki']:
    model_name = {'mm': 'MiniMax', 'ds': 'DeepSeek', 'ki': 'Kimi'}[model]
    anchors = Counter(r[model + '_anchor'] for r in informative)
    print(f"\n  {model_name}:")
    for k, v in anchors.most_common():
        print(f"    {k:20s}: {v:3d}")

# All cases (including same)
print(f"\nAll {len(results)} cases:")
for model in ['mm', 'ds', 'ki']:
    model_name = {'mm': 'MiniMax', 'ds': 'DeepSeek', 'ki': 'Kimi'}[model]
    anchors = Counter(r[model + '_anchor'] for r in results)
    print(f"\n  {model_name}:")
    for k, v in anchors.most_common():
        print(f"    {k:20s}: {v:3d}")

# Canon anchor
print(f"\nCanon resolution anchor (all {len(results)}):")
canon_anchors = Counter()
for r in results:
    cv = r['canon']
    if cv not in set(r['scan'].keys()):
        canon_anchors['NOT_IN_TEXT'] += 1
    elif r['same_first_and_most']:
        canon_anchors['BOTH_SAME'] += 1
    elif cv == r['first_mentioned_cat']:
        canon_anchors['FIRST_MENTIONED'] += 1
    elif cv == r['most_discussed_cat']:
        canon_anchors['MOST_DISCUSSED'] += 1
    else:
        canon_anchors['OTHER_CAT'] += 1
print(f"  {dict(canon_anchors)}")

# ---- Print case-by-case detail for informative cases ----
print("\n" + "=" * 70)
print("CASE-BY-CASE DETAIL (first != most)")
print("=" * 70)
for r in informative:
    print(f"\n  {r['case_name']}")
    print(f"    Outcome: {r['outcome']}")
    print(f"    MM={r['mm']:30s} -> {r['mm_anchor']}")
    print(f"    DS={r['ds']:30s} -> {r['ds_anchor']}")
    print(f"    KI={r['ki']:30s} -> {r['ki_anchor']}")
    print(f"    Canon={r['canon']}")
    print(f"    First mentioned: {r['first_mentioned_cat']}")
    print(f"    Most discussed:  {r['most_discussed_cat']}")
    for cat, s in r['scan'].items():
        print(f"      {cat:35s} pos={s['first_pos_pct']:5.1f}%  mentions={s['mentions']:3d}  density={s['density']}")

with open(os.path.join(RESULTS_DIR, 'positional_bias_analysis.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(results)} results to positional_bias_analysis.json")
