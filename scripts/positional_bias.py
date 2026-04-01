import json, re, os
from collections import Counter, defaultdict

with open('C:/Users/nickg/IdeaProjects/MFH-Java-Work/allFHAcases/recentcases/RAClassification_DB_resolved_20260328_085823.json', encoding='utf-8') as f:
    resolved = json.load(f)

CATEGORY_KEYWORDS = {
    'ASSISTANCE_ANIMAL': ['assistance animal', 'emotional support animal', 'esa', 'service animal', 'service dog', 'companion animal', 'support animal', 'no-pet', 'no pet', 'pet policy'],
    'PARKING': ['parking', 'designated spot', 'handicap space', 'reserved space', 'accessible parking'],
    'STRUCTURAL_MODIFICATION': ['ramp', 'grab bar', 'wheelchair', 'widened door', 'roll-in shower', 'handrail', 'structural modification', 'physical modification', 'railing'],
    'TRANSFER': ['unit transfer', 'transfer to', 'relocat', 'different unit', 'move to another', 'accessible unit', 'ground floor', 'first floor unit'],
    'EVICTION_DEFENSE': ['eviction', 'evict', 'lease termination', 'notice to quit', 'second chance', 'cure period'],
    'LIVE_IN_AIDE': ['live-in aide', 'live in aide', 'caregiver', 'additional occupant', 'personal care attendant'],
    'SOBER_LIVING_GROUP_HOME_ZONING': ['sober living', 'group home', 'recovery home', 'halfway house', 'zoning', 'oxford house'],
    'COMMUNICATION_ACCOMMODATION': ['large print', 'interpreter', 'written notice', 'braille', 'communication accommodation', 'accessible format'],
    'RENT_PAYMENT': ['rent payment', 'payment plan', 'late fee', 'rent accommodation', 'rental assistance'],
    'POLICY_EXCEPTION': ['policy exception', 'waiver', 'exception to', 'modify policy', 'rule exception', 'policy modification', 'reasonable modification'],
}

def scan_text(text):
    text_lower = text.lower()
    text_len = len(text_lower)
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
            best_density = 0
            for p in positions:
                ws = max(0, p - 500)
                we = min(text_len, p + 500)
                c = sum(1 for pp in positions if ws <= pp <= we)
                d = c / ((we - ws) / 1000) if we > ws else 0
                best_density = max(best_density, d)
            results[cat] = {
                'first_mention': positions[0],
                'first_mention_pct': positions[0] / text_len * 100,
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
        'COMMUNICATION': ['notice', 'large print', 'interpreter'],
        'RENT_PAYMENT': ['rent', 'payment plan', 'late fee'],
    }
    for cat, kws in simple.items():
        for kw in kws:
            if kw in tl:
                found.add(cat)
                break
    return found

targets = []
for r in resolved:
    if len(desc_types(r)) < 2:
        continue
    mm = r.get('accommodation_type_minmax', '').strip().upper()
    ds = r.get('accommodation_type_deepseek', '').strip().upper()
    ki = r.get('accommodation_type_kimi', '').strip().upper()
    specific = [m for m in [mm, ds, ki] if m not in ('UNDETERMINED', 'OTHER', 'NONE', 'DISCRIMINATION_PRIMARY', '')]
    if len(set(specific)) < 2:
        continue
    targets.append(r)

print(f"Target cases: {len(targets)}")

CASE_DIR = 'C:/Users/nickg/IdeaProjects/MFH-Java-Work/allFHAcases/recentcases'
results = []

for tc in targets:
    sf = tc.get('source_file', '')
    txt_path = os.path.join(CASE_DIR, sf + '.txt')
    if not os.path.exists(txt_path):
        continue

    with open(txt_path, encoding='utf-8', errors='replace') as f:
        text = f.read()

    scan = scan_text(text)
    mm = tc.get('accommodation_type_minmax', '').strip().upper()
    ds = tc.get('accommodation_type_deepseek', '').strip().upper()
    ki = tc.get('accommodation_type_kimi', '').strip().upper()
    canon = tc.get('accommodation_type', '').strip().upper()

    model_cats = set(m for m in [mm, ds, ki] if m in scan)
    if len(model_cats) < 2:
        continue

    first_mentioned = min(model_cats, key=lambda c: scan[c]['first_mention'])
    most_discussed = max(model_cats, key=lambda c: scan[c]['total_mentions'])

    cr = {
        'case_name': tc.get('case_name', '')[:70],
        'source_file': sf,
        'outcome': tc.get('outcome', ''),
        'mm': mm, 'ds': ds, 'ki': ki, 'canon': canon,
        'first_mentioned_cat': first_mentioned,
        'most_discussed_cat': most_discussed,
        'same_first_and_most': first_mentioned == most_discussed,
        'scan': {},
    }

    for cat in model_cats:
        s = scan[cat]
        cr['scan'][cat] = {
            'first_pos_pct': round(s['first_mention_pct'], 1),
            'mentions': s['total_mentions'],
            'density': s['peak_density'],
        }

    for mn, mv in [('mm', mm), ('ds', ds), ('ki', ki)]:
        if first_mentioned == most_discussed:
            cr[mn + '_anchor'] = 'BOTH_SAME' if mv == first_mentioned else 'NEITHER'
        elif mv == first_mentioned:
            cr[mn + '_anchor'] = 'FIRST_MENTIONED'
        elif mv == most_discussed:
            cr[mn + '_anchor'] = 'MOST_DISCUSSED'
        else:
            cr[mn + '_anchor'] = 'NEITHER'

    results.append(cr)

print(f"Scannable cases with 2+ model cats found: {len(results)}")
print(f"Cases where first != most: {sum(1 for r in results if not r['same_first_and_most'])}")

with open('C:/Users/nickg/OneDrive/Documents/Note/positional_bias_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("Saved positional_bias_analysis.json")
