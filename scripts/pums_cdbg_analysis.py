"""
Estimate disabled renters of color living outside CDBG entitlement jurisdictions.

Uses ACS 2022 5-Year place-level data from the Census Bureau API.
Entitlement jurisdictions approximated as places with population >= 50,000.

Key tables:
- B01003: Total population
- B25003 + race iterations: Tenure by race of householder
- B18101: Sex by age by disability status (main table)
  "With disability" vars: Male _004,_007,_010,_013,_016,_019
                          Female _023,_026,_029,_032,_035,_038
- B18101B/C/D/F/G/H/I: Race-iterated disability (simpler structure)
  "With disability" vars: _003, _006, _009

No single table cross-tabs disability x race x tenure, so we estimate
via independence assumption.
"""

import urllib.request
import json
import time
import sys

BASE_URL = "https://api.census.gov/data/2022/acs/acs5"


def census_query(get_vars, geo_for, geo_in=None, retries=3):
    """Query Census API and return parsed JSON."""
    url = f"{BASE_URL}?get={get_vars}&for={geo_for}"
    if geo_in:
        url += f"&in={geo_in}"

    for attempt in range(retries):
        try:
            print(f"  Querying: ...{get_vars[:80]}... &for={geo_for}")
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "Mozilla/5.0 (research script)")
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
            print(f"  => {len(data)-1} rows")
            return data
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(3)
    return None


def safe_int(val):
    if val is None:
        return 0
    try:
        v = int(val)
        return 0 if v < 0 else v
    except (ValueError, TypeError):
        return 0


def build_lookup(api_data):
    """Return (header_list, dict keyed by (state, place) -> row_dict)."""
    hdr = api_data[0]
    si, pi = hdr.index("state"), hdr.index("place")
    lookup = {}
    for row in api_data[1:]:
        key = (row[si], row[pi])
        lookup[key] = {h: row[i] for i, h in enumerate(hdr)}
    return hdr, lookup


def main():
    print("=" * 72)
    print("CDBG ENTITLEMENT ANALYSIS: Disabled Renters of Color")
    print("Data: ACS 2022 5-Year Estimates, Place Level")
    print("=" * 72)

    # ==================================================================
    # STEP 1 - Population -> classify places
    # ==================================================================
    print("\n[STEP 1] Fetching total population for all places...")
    pop_raw = census_query("NAME,B01003_001E", "place:*", "state:*")
    if not pop_raw:
        sys.exit("FATAL: Could not get population data.")

    _, pop_lk = build_lookup(pop_raw)
    places = {k: safe_int(v["B01003_001E"]) for k, v in pop_lk.items()}

    entitlement = {k for k, p in places.items() if p >= 50000}
    non_entitlement = {k for k, p in places.items() if p < 50000}
    ent_pop = sum(places[k] for k in entitlement)
    nent_pop = sum(places[k] for k in non_entitlement)

    print(f"\n  Total places: {len(places):,}")
    print(f"  Entitlement (>=50K): {len(entitlement):,} places, pop {ent_pop:,}")
    print(f"  Non-entitlement (<50K): {len(non_entitlement):,} places, pop {nent_pop:,}")

    # ==================================================================
    # STEP 2 - Tenure by race of householder
    # ==================================================================
    print("\n[STEP 2] Fetching tenure by race of householder...")
    tenure_vars = (
        "B25003_001E,B25003_002E,B25003_003E,"
        "B25003A_003E,B25003B_003E,B25003C_003E,"
        "B25003D_003E,B25003E_003E,B25003F_003E,"
        "B25003G_003E,B25003H_003E,B25003I_003E"
    )
    ten_raw = census_query(tenure_vars, "place:*", "state:*")
    if not ten_raw:
        sys.exit("FATAL: Could not get tenure data.")

    _, ten_lk = build_lookup(ten_raw)

    labels_map = {
        "total": "B25003_003E",
        "owners": "B25003_002E",
        "white_alone": "B25003A_003E",
        "black": "B25003B_003E",
        "aian": "B25003C_003E",
        "asian": "B25003D_003E",
        "nhpi": "B25003E_003E",
        "other": "B25003F_003E",
        "two_plus": "B25003G_003E",
        "white_nh": "B25003H_003E",
        "hispanic": "B25003I_003E",
    }

    def sum_tenure(key_set):
        acc = {k: 0 for k in labels_map}
        for k in key_set:
            if k in ten_lk:
                row = ten_lk[k]
                for lbl, var in labels_map.items():
                    acc[lbl] += safe_int(row.get(var))
        return acc

    ent_r = sum_tenure(entitlement)
    nent_r = sum_tenure(non_entitlement)

    ent_roc = ent_r["total"] - ent_r["white_nh"]
    nent_roc = nent_r["total"] - nent_r["white_nh"]
    total_roc = ent_roc + nent_roc

    print("\n  --- RENTER COUNTS ---")
    fmt = "  {:<40} {:>14,} {:>16,} {:>14,}"
    print(f"  {'Category':<40} {'Entitlement':>14} {'Non-Entitlement':>16} {'Total':>14}")
    print(f"  {'-'*86}")
    print(fmt.format("Total renters", ent_r["total"], nent_r["total"], ent_r["total"]+nent_r["total"]))
    print(fmt.format("White non-Hispanic renters", ent_r["white_nh"], nent_r["white_nh"], ent_r["white_nh"]+nent_r["white_nh"]))
    print(fmt.format("Renters of color (total - WNH)", ent_roc, nent_roc, total_roc))
    for lbl, tag in [("Black/Afr. American", "black"), ("AIAN", "aian"),
                     ("Asian", "asian"), ("NHPI", "nhpi"),
                     ("Some other race", "other"), ("Two+ races", "two_plus"),
                     ("Hispanic/Latino", "hispanic")]:
        print(fmt.format(f"  {lbl} renters", ent_r[tag], nent_r[tag], ent_r[tag]+nent_r[tag]))
    print(fmt.format("Total owners", ent_r["owners"], nent_r["owners"], ent_r["owners"]+nent_r["owners"]))

    if total_roc:
        print(f"\n  Share of ROC renters in non-entitlement: {nent_roc/total_roc*100:.1f}%")
    if nent_r["total"]:
        print(f"  ROC share of all non-entitlement renters: {nent_roc/nent_r['total']*100:.1f}%")

    # ==================================================================
    # STEP 3 - Disability (main table B18101, all races)
    # ==================================================================
    print("\n[STEP 3] Fetching disability status (B18101, all races)...")

    # Correct "with disability" variable IDs for B18101:
    # Male: Under5=_004, 5-17=_007, 18-34=_010, 35-64=_013, 65-74=_016, 75+=_019
    # Female: Under5=_023, 5-17=_026, 18-34=_029, 35-64=_032, 65-74=_035, 75+=_038
    dis_vars_male = ["B18101_004E","B18101_007E","B18101_010E",
                     "B18101_013E","B18101_016E","B18101_019E"]
    dis_vars_female = ["B18101_023E","B18101_026E","B18101_029E",
                       "B18101_032E","B18101_035E","B18101_038E"]
    all_dis_vars = dis_vars_male + dis_vars_female

    dis_str = "B18101_001E," + ",".join(all_dis_vars)
    dis_raw = census_query(dis_str, "place:*", "state:*")
    if not dis_raw:
        sys.exit("FATAL: Could not get disability data.")

    _, dis_lk = build_lookup(dis_raw)

    def sum_disability(key_set, lookup, vars_list, total_var="B18101_001E"):
        tot_u, tot_d = 0, 0
        for k in key_set:
            if k in lookup:
                row = lookup[k]
                tot_u += safe_int(row.get(total_var))
                tot_d += sum(safe_int(row.get(v)) for v in vars_list)
        return tot_u, tot_d

    ent_du, ent_d = sum_disability(entitlement, dis_lk, all_dis_vars)
    nent_du, nent_d = sum_disability(non_entitlement, dis_lk, all_dis_vars)
    total_d = ent_d + nent_d
    total_du = ent_du + nent_du

    print(f"\n  --- DISABILITY COUNTS (all races) ---")
    print(f"  {'Category':<42} {'Entitlement':>14} {'Non-Entitlement':>16} {'Total':>14}")
    print(f"  {'-'*88}")
    print(f"  {'Disability universe (civ. noninst.)':<42} {ent_du:>14,} {nent_du:>16,} {total_du:>14,}")
    print(f"  {'With any disability':<42} {ent_d:>14,} {nent_d:>16,} {total_d:>14,}")
    if ent_du and nent_du:
        print(f"  {'Disability rate':<42} {ent_d/ent_du*100:>13.1f}% {nent_d/nent_du*100:>15.1f}% {total_d/total_du*100:>13.1f}%")
    if total_d:
        print(f"\n  Share of disabled pop in non-entitlement: {nent_d/total_d*100:.1f}%")

    # ==================================================================
    # STEP 4 - Disability by race (race-iterated B18101 tables)
    # ==================================================================
    print("\n[STEP 4] Fetching disability by race (race-iterated tables)...")

    # Race-iterated tables have SIMPLER structure (no sex breakdown):
    #   _001: Total
    #   _002: Under 18
    #   _003: Under 18, With a disability
    #   _004: Under 18, No disability
    #   _005: 18 to 64
    #   _006: 18 to 64, With a disability
    #   _007: 18 to 64, No disability
    #   _008: 65 and over
    #   _009: 65 and over, With a disability
    #   _010: 65 and over, No disability

    race_tables = [
        ("B", "Black/Afr. American"),
        ("C", "AIAN"),
        ("D", "Asian"),
        ("F", "Some other race"),
        ("G", "Two or more races"),
        ("H", "White non-Hispanic"),
        ("I", "Hispanic/Latino"),
    ]

    race_dis = {}  # label -> {ent_d, nent_d, ent_u, nent_u}

    for suffix, label in race_tables:
        tbl = f"B18101{suffix}"
        dis_v = [f"{tbl}_003E", f"{tbl}_006E", f"{tbl}_009E"]
        qstr = f"{tbl}_001E," + ",".join(dis_v)

        rdata = census_query(qstr, "place:*", "state:*")
        if not rdata:
            print(f"    FAILED for {tbl}, skipping {label}.")
            continue
        time.sleep(0.5)  # be polite to API

        _, rlk = build_lookup(rdata)

        e_u, e_d = 0, 0
        n_u, n_d = 0, 0
        for k in rlk:
            row = rlk[k]
            u = safe_int(row.get(f"{tbl}_001E"))
            d = sum(safe_int(row.get(v)) for v in dis_v)
            if k in entitlement:
                e_u += u; e_d += d
            else:
                n_u += u; n_d += d

        race_dis[label] = {"ent_d": e_d, "nent_d": n_d, "ent_u": e_u, "nent_u": n_u}

    print(f"\n  --- DISABLED POPULATION BY RACE ---")
    print(f"  {'Race':<25} {'Ent. Disabled':>14} {'Non-Ent. Disabled':>18} {'Total':>12} {'% Non-Ent':>10}")
    print(f"  {'-'*80}")
    for label, v in race_dis.items():
        t = v["ent_d"] + v["nent_d"]
        pct = v["nent_d"]/t*100 if t else 0
        print(f"  {label:<25} {v['ent_d']:>14,} {v['nent_d']:>18,} {t:>12,} {pct:>9.1f}%")
        # Also print disability rate
        if v["ent_u"] and v["nent_u"]:
            er = v["ent_d"]/v["ent_u"]*100
            nr = v["nent_d"]/v["nent_u"]*100
            print(f"  {'  (disability rate)':<25} {er:>13.1f}% {nr:>17.1f}%")

    # ==================================================================
    # STEP 5 - Estimation
    # ==================================================================
    print("\n" + "=" * 72)
    print("ESTIMATES: Disabled Renters of Color Outside Entitlement Jurisdictions")
    print("=" * 72)

    ent_hh = ent_r["total"] + ent_r["owners"]
    nent_hh = nent_r["total"] + nent_r["owners"]
    ent_rr = ent_r["total"] / ent_hh if ent_hh else 0
    nent_rr = nent_r["total"] / nent_hh if nent_hh else 0

    print(f"\n  Renter rate (all HH) - entitlement: {ent_rr*100:.1f}%")
    print(f"  Renter rate (all HH) - non-entitlement: {nent_rr*100:.1f}%")

    # Race-specific renter rates in non-entitlement
    # From Step 2 we have race-specific renter counts; we need race-specific owner counts too
    # B25003X_002E = owners for race X. Let's compute renter rates per race.
    # We didn't query owner counts by race. We have renter counts by race.
    # We can estimate: for non-entitlement, renter share for each race group.
    # But we only have renter counts, not total HH by race.
    # Use overall non-entitlement renter rate as proxy.

    wnh_ent_d = race_dis.get("White non-Hispanic", {}).get("ent_d", 0)
    wnh_nent_d = race_dis.get("White non-Hispanic", {}).get("nent_d", 0)

    poc_ent_d = ent_d - wnh_ent_d
    poc_nent_d = nent_d - wnh_nent_d
    poc_total_d = poc_ent_d + poc_nent_d

    print(f"\n  Disabled persons of color (total disabled - White NH disabled):")
    print(f"    Entitlement:     {poc_ent_d:>12,}")
    print(f"    Non-entitlement: {poc_nent_d:>12,}")
    print(f"    Total:           {poc_total_d:>12,}")
    if poc_total_d:
        print(f"    % in non-ent:    {poc_nent_d/poc_total_d*100:>11.1f}%")

    # Estimate disabled renters of color
    # Method A: disability_rate_by_race * race_renter_count (for non-ent)
    # We have disability rates by race from Step 4 and renter counts by race from Step 2

    print("\n  --- METHOD A: Race-specific disability rate x renter count ---")
    print(f"  {'Race':<25} {'Nent Renters':>13} {'Dis. Rate':>10} {'Est. Dis. Renters':>18}")
    print(f"  {'-'*68}")

    race_renter_map = {
        "Black/Afr. American": nent_r["black"],
        "AIAN": nent_r["aian"],
        "Asian": nent_r["asian"],
        "NHPI": nent_r["nhpi"],
        "Some other race": nent_r["other"],
        "Two or more races": nent_r["two_plus"],
        "Hispanic/Latino": nent_r["hispanic"],
        "White non-Hispanic": nent_r["white_nh"],
    }

    est_a_nent_poc = 0
    est_a_nent_total = 0
    for label in race_renter_map:
        renters = race_renter_map[label]
        if label in race_dis and race_dis[label]["nent_u"] > 0:
            dis_rate = race_dis[label]["nent_d"] / race_dis[label]["nent_u"]
        else:
            dis_rate = nent_d / nent_du if nent_du else 0  # fallback

        est = int(renters * dis_rate)
        est_a_nent_total += est
        if label != "White non-Hispanic":
            est_a_nent_poc += est
            print(f"  {label:<25} {renters:>13,} {dis_rate:>9.1%} {est:>18,}")

    print(f"  {'-'*68}")
    print(f"  {'TOTAL POC':<25} {nent_roc:>13,} {'':>10} {est_a_nent_poc:>18,}")
    print(f"  {'White NH (reference)':<25} {nent_r['white_nh']:>13,} {'':>10} {est_a_nent_total - est_a_nent_poc:>18,}")

    # Same for entitlement
    est_a_ent_poc = 0
    race_renter_map_ent = {
        "Black/Afr. American": ent_r["black"],
        "AIAN": ent_r["aian"],
        "Asian": ent_r["asian"],
        "NHPI": ent_r["nhpi"],
        "Some other race": ent_r["other"],
        "Two or more races": ent_r["two_plus"],
        "Hispanic/Latino": ent_r["hispanic"],
    }
    for label in race_renter_map_ent:
        renters = race_renter_map_ent[label]
        if label in race_dis and race_dis[label]["ent_u"] > 0:
            dis_rate = race_dis[label]["ent_d"] / race_dis[label]["ent_u"]
        else:
            dis_rate = ent_d / ent_du if ent_du else 0
        est_a_ent_poc += int(renters * dis_rate)

    est_a_total_poc = est_a_ent_poc + est_a_nent_poc

    # Method B: simpler - apply overall renter rate to disabled POC
    est_b_nent = int(poc_nent_d * nent_rr)
    est_b_ent = int(poc_ent_d * ent_rr)
    est_b_total = est_b_nent + est_b_ent

    print(f"\n  --- METHOD B: Overall renter rate x disabled POC ---")
    print(f"  Non-ent disabled POC ({poc_nent_d:,}) x renter rate ({nent_rr:.1%}) = ~{est_b_nent:,}")
    print(f"  Ent disabled POC ({poc_ent_d:,}) x renter rate ({ent_rr:.1%}) = ~{est_b_ent:,}")
    print(f"  Total: ~{est_b_total:,}")

    # ==================================================================
    # FINAL SUMMARY
    # ==================================================================
    print(f"\n{'=' * 72}")
    print("FINAL SUMMARY")
    print(f"{'=' * 72}")

    print(f"""
  GEOGRAPHY:
    Census places >= 50K pop (entitlement proxy): {len(entitlement):,} places, {ent_pop:,} people
    Census places < 50K pop (non-entitlement):    {len(non_entitlement):,} places, {nent_pop:,} people
    Note: ~80M people live outside any Census place (unincorporated) = also non-entitlement

  RENTERS OF COLOR (from B25003 race iterations):
    All places:           {total_roc:>12,}
    Entitlement:          {ent_roc:>12,}  ({ent_roc/total_roc*100:.1f}%)
    Non-entitlement:      {nent_roc:>12,}  ({nent_roc/total_roc*100:.1f}%)

  DISABLED POPULATION (from B18101, all races, both sexes):
    All places:           {total_d:>12,}
    Entitlement:          {ent_d:>12,}  ({ent_d/total_d*100:.1f}%)
    Non-entitlement:      {nent_d:>12,}  ({nent_d/total_d*100:.1f}%)

  DISABLED PERSONS OF COLOR (total disabled - White NH disabled):
    All places:           {poc_total_d:>12,}
    Entitlement:          {poc_ent_d:>12,}  ({poc_ent_d/poc_total_d*100:.1f}%)
    Non-entitlement:      {poc_nent_d:>12,}  ({poc_nent_d/poc_total_d*100:.1f}%)

  ESTIMATED DISABLED RENTERS OF COLOR:
    Method A (race-specific disability rates x race-specific renter counts):
      Entitlement:        ~{est_a_ent_poc:>11,}
      Non-entitlement:    ~{est_a_nent_poc:>11,}
      Total:              ~{est_a_total_poc:>11,}
      % in non-entitlement: ~{est_a_nent_poc/est_a_total_poc*100 if est_a_total_poc else 0:.1f}%

    Method B (overall renter rate x disabled POC):
      Entitlement:        ~{est_b_ent:>11,}
      Non-entitlement:    ~{est_b_nent:>11,}
      Total:              ~{est_b_total:>11,}
      % in non-entitlement: ~{est_b_nent/est_b_total*100 if est_b_total else 0:.1f}%

  KEY RACE BREAKDOWNS IN NON-ENTITLEMENT PLACES:
    Black renters:        {nent_r['black']:>12,}  (of {nent_r['black']+ent_r['black']:,} total)
    AIAN renters:         {nent_r['aian']:>12,}  (of {nent_r['aian']+ent_r['aian']:,} total)
    Hispanic renters:     {nent_r['hispanic']:>12,}  (of {nent_r['hispanic']+ent_r['hispanic']:,} total)
    Asian renters:        {nent_r['asian']:>12,}  (of {nent_r['asian']+ent_r['asian']:,} total)

  CAVEATS:
    1. "Entitlement" = places >= 50K (proxy). Actual CDBG entitlement includes
       urban counties and some metro cities < 50K.
    2. ~80M people in unincorporated areas are NOT captured in place-level data.
       These are also non-entitlement, so our non-entitlement figures are
       UNDERCOUNTS.
    3. Independence assumption: disability rate among renters may differ from
       overall disability rate. Research shows disabled persons rent at HIGHER
       rates, so Method A/B may be conservative.
    4. Hispanic overlaps with race categories (Black, AIAN, etc.) -- the
       race-iteration tables (B suffix) use race-alone, while I suffix uses
       ethnicity. The "total - White NH" approach avoids double-counting.
    5. All figures have margins of error (not shown).
""")

    print("Done.")


if __name__ == "__main__":
    main()
