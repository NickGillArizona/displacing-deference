"""
Census PUMS Replication Script
================================
Replicates the ACS 2020-2024 5-Year PUMS estimates reported in the Note.

Data Source: U.S. Census Bureau, American Community Survey 2020-2024 5-Year
Public Use Microdata Sample (PUMS), accessed via the Census Bureau Data API.

API Endpoint: https://api.census.gov/data/2024/acs/acs5/pums
No API key required.

Variable Definitions:
  SPORDER = 1 (householder only)
  TEN = 3 (rented)
  RAC1P: 1=White alone, 2=Black/AA alone, 3=AIAN alone
  DPHY: 1=Ambulatory difficulty, 2=No
  DOUT: 1=Independent living difficulty, 2=No
  GRPIP: Gross rent as % of household income (1-100; 101=not computed)
  HINCP: Household income (past 12 months, integer, can be negative)
  PWGTP: Person weight (integer)

Disability definition: DPHY=1 OR DOUT=1 (ambulatory or independent living difficulty)
Cost burden: GRPIP > 30 (excluding GRPIP=101)

Analysis conducted March 27, 2026.
"""

import urllib.request
import json
import sys

BASE_URL = "https://api.census.gov/data/2024/acs/acs5/pums"
RACE_LABELS = {1: "White alone", 2: "Black/AA alone", 3: "AIAN alone"}


def fetch_pums(variables: str, filters: str = "") -> list:
    """Fetch PUMS data from Census API."""
    url = f"{BASE_URL}?get=PWGTP,{variables}&for=state:*&SPORDER=1&TEN=3{filters}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    return data


def is_disabled(row: list, dphy_idx: int, dout_idx: int) -> bool:
    """Check if householder has ambulatory or independent living difficulty."""
    return row[dphy_idx] == "1" or row[dout_idx] == "1"


def query_disability_prevalence():
    """
    Query 1: Disability Prevalence by Race
    Supports Part II.E, paragraph 2, and footnote [72].
    GET ...?get=PWGTP,DPHY,DOUT&for=state:*&SPORDER=1&TEN=3&RAC1P={1,2,3}
    """
    print("=" * 60)
    print("Query 1: Disability Prevalence by Race")
    print("=" * 60)

    for race_code, race_label in RACE_LABELS.items():
        data = fetch_pums("DPHY,DOUT", f"&RAC1P={race_code}")
        header = data[0]
        rows = data[1:]

        pwgtp_idx = header.index("PWGTP")
        dphy_idx = header.index("DPHY")
        dout_idx = header.index("DOUT")

        total_weight = sum(int(r[pwgtp_idx]) for r in rows)
        disabled_weight = sum(
            int(r[pwgtp_idx]) for r in rows if is_disabled(r, dphy_idx, dout_idx)
        )
        prevalence = disabled_weight / total_weight * 100

        print(f"  {race_label}: {prevalence:.2f}% "
              f"(n={len(rows):,}, weighted={total_weight:,}, disabled={disabled_weight:,})")


def query_cost_burden():
    """
    Query 2: Cost Burden by Disability Status and Race
    Supports Part II.E, paragraph 1, and footnotes [68a] and [71].
    GET ...?get=PWGTP,DPHY,DOUT,GRPIP&for=state:*&SPORDER=1&TEN=3&RAC1P={1,2,3}
    """
    print("\n" + "=" * 60)
    print("Query 2: Cost Burden by Disability Status and Race")
    print("=" * 60)

    for race_code, race_label in RACE_LABELS.items():
        data = fetch_pums("DPHY,DOUT,GRPIP", f"&RAC1P={race_code}")
        header = data[0]
        rows = data[1:]

        pwgtp_idx = header.index("PWGTP")
        dphy_idx = header.index("DPHY")
        dout_idx = header.index("DOUT")
        grpip_idx = header.index("GRPIP")

        disabled_total = 0
        disabled_burdened = 0
        nondisabled_total = 0
        nondisabled_burdened = 0

        for r in rows:
            weight = int(r[pwgtp_idx])
            grpip = int(r[grpip_idx])
            disabled = is_disabled(r, dphy_idx, dout_idx)

            # Exclude GRPIP=101 (not computed)
            if grpip == 101:
                continue

            if disabled:
                disabled_total += weight
                if grpip > 30:
                    disabled_burdened += weight
            else:
                nondisabled_total += weight
                if grpip > 30:
                    nondisabled_burdened += weight

        dis_rate = disabled_burdened / disabled_total * 100 if disabled_total else 0
        nondis_rate = nondisabled_burdened / nondisabled_total * 100 if nondisabled_total else 0
        penalty = dis_rate - nondis_rate

        print(f"  {race_label}:")
        print(f"    Disabled CB rate:     {dis_rate:.1f}%")
        print(f"    Non-disabled CB rate: {nondis_rate:.1f}%")
        print(f"    Disability penalty:   {penalty:.1f} pp")


def query_grpip101():
    """
    Query 3: GRPIP=101 Rate by Race
    Supports Part II.E, paragraph 5, and footnotes [58] and [177].
    GET ...?get=PWGTP,DPHY,DOUT,HINCP,GRPIP&for=state:*&SPORDER=1&TEN=3&RAC1P={1,2,3}
    """
    print("\n" + "=" * 60)
    print("Query 3: GRPIP=101 Rate by Race (Disabled Renters)")
    print("=" * 60)

    for race_code, race_label in RACE_LABELS.items():
        data = fetch_pums("DPHY,DOUT,HINCP,GRPIP", f"&RAC1P={race_code}")
        header = data[0]
        rows = data[1:]

        pwgtp_idx = header.index("PWGTP")
        dphy_idx = header.index("DPHY")
        dout_idx = header.index("DOUT")
        hincp_idx = header.index("HINCP")
        grpip_idx = header.index("GRPIP")

        total_disabled = 0
        grpip101_total = 0
        grpip101_neg_income = 0

        for r in rows:
            weight = int(r[pwgtp_idx])
            if not is_disabled(r, dphy_idx, dout_idx):
                continue

            total_disabled += weight
            grpip = int(r[grpip_idx])
            if grpip == 101:
                grpip101_total += weight
                hincp = int(r[hincp_idx])
                if hincp <= 0:
                    grpip101_neg_income += weight

        rate = grpip101_total / total_disabled * 100 if total_disabled else 0
        neg_rate = grpip101_neg_income / total_disabled * 100 if total_disabled else 0
        pos_rate = rate - neg_rate

        print(f"  {race_label}:")
        print(f"    GRPIP=101 rate:       {rate:.1f}%")
        print(f"    Of which HINCP <= 0:  {neg_rate:.1f}%")
        print(f"    Of which HINCP > 0:   {pos_rate:.1f}%")


def query_hispanic_analysis():
    """
    Query 4: Hispanic/Latino PUMS Analysis (Appendix A-3, Section E)
    GET ...?get=PWGTP,DPHY,DOUT,GRPIP,RAC1P,HISP&for=state:*&SPORDER=1&TEN=3
    """
    print("\n" + "=" * 60)
    print("Query 4: Hispanic/Latino Disability Penalty Analysis")
    print("=" * 60)

    data = fetch_pums("DPHY,DOUT,GRPIP,RAC1P,HISP")
    header = data[0]
    rows = data[1:]

    pwgtp_idx = header.index("PWGTP")
    dphy_idx = header.index("DPHY")
    dout_idx = header.index("DOUT")
    grpip_idx = header.index("GRPIP")
    rac1p_idx = header.index("RAC1P")
    hisp_idx = header.index("HISP")

    # Categories: NH-White, NH-Black, NH-AIAN, Hispanic (any race)
    categories = {
        "Non-Hispanic White": lambda r: r[rac1p_idx] == "1" and r[hisp_idx] == "01",
        "Non-Hispanic Black": lambda r: r[rac1p_idx] == "2" and r[hisp_idx] == "01",
        "Non-Hispanic AIAN": lambda r: r[rac1p_idx] == "3" and r[hisp_idx] == "01",
        "Hispanic (any race)": lambda r: r[hisp_idx] != "01",
    }

    for cat_label, cat_filter in categories.items():
        dis_total = dis_burdened = nondis_total = nondis_burdened = 0
        for r in rows:
            if not cat_filter(r):
                continue
            weight = int(r[pwgtp_idx])
            grpip = int(r[grpip_idx])
            if grpip == 101:
                continue
            disabled = is_disabled(r, dphy_idx, dout_idx)
            if disabled:
                dis_total += weight
                if grpip > 30:
                    dis_burdened += weight
            else:
                nondis_total += weight
                if grpip > 30:
                    nondis_burdened += weight

        dis_rate = dis_burdened / dis_total * 100 if dis_total else 0
        nondis_rate = nondis_burdened / nondis_total * 100 if nondis_total else 0
        penalty = dis_rate - nondis_rate
        print(f"  {cat_label}: penalty = {penalty:.1f} pp "
              f"(disabled {dis_rate:.1f}%, non-disabled {nondis_rate:.1f}%)")


if __name__ == "__main__":
    print("FHA Disability Housing Cost-Burden Replication")
    print("Data: ACS 2020-2024 5-Year PUMS")
    print()

    query_disability_prevalence()
    query_cost_burden()
    query_grpip101()
    query_hispanic_analysis()

    print("\n" + "=" * 60)
    print("Replication complete.")
    print("Source: U.S. Census Bureau, ACS 2020-2024 5-Year PUMS")
    print("API: https://api.census.gov/data/2024/acs/acs5/pums")
