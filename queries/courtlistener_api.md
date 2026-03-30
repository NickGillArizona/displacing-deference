# CourtListener REST API (v4) — Case Download Queries

Source code for the full download pipeline is in the companion repository:
[MFH-Java-Work](https://github.com/NickGillArizona/MFH-Java-Work)

Key Java classes:
- `src/main/java/mfh/gfo/CourtListenerFHADownloader.java` — Primary download pipeline
- `src/main/java/mfh/gfo/CourtListenerClient.java` — API client
- `src/main/java/mfh/gfo/CourtListenerOpinionClient.java` — Opinion text retrieval
- `src/main/java/mfh/gfo/CourtListenerOpinionClient_NoteVersion.java` — Note-specific variant

---

## RA Database Query (n=1,857)

**Endpoint:** CourtListener REST API v4 search

**Parameters:**
- Query: exact phrase `"fair housing act"`
- Courts: all federal (Supreme Court, all circuits, all districts)
- Filing date: after January 1, 2021
- Status: published, unpublished, and unknown
- Deduplication: by cluster ID
- Retrieval: 10-thread parallel from opinions endpoint

**Resulting corpus:** 2,366 documents (1,857 passed FHA screening)

---

## 2015 FHA Database Query (n=1,496)

**Endpoint:** CourtListener REST API v4 search + Google Scholar supplement

**Parameters:**
- Query: exact phrase `"fair housing act"`
- Courts: all federal
- Filing date: after January 1, 2015
- Status: published, unpublished, and unknown
- Deduplication: by cluster ID
- Supplement: 215 case texts from Google Scholar (post-2024 cases not indexed in CourtListener)

**Resulting corpus:** 1,661 documents (1,496 passed FHA screening)

---

## FHA Pilot Database Query (n=331)

**Parameters:**
- Query: all three terms required — `"fair housing act"`, `"race"`, `"zoning"`
- Courts: all federal
- Filing date: 2012-2026
- Deduplication: by cluster ID

**Resulting corpus:** 331 documents

---

## Pipeline Architecture

```
CourtListener API ──┬── Download (Java, 10-thread parallel)
                    │
                    ├── FHA Screening (Gemini 3.1 Flash Lite, temp=0.0)
                    │   └── Binary YES/NO filter
                    │
                    ├── Triple-Model Classification (OpenRouter API)
                    │   ├── MiniMax M2.7 (primary, reasoning=2048)
                    │   ├── DeepSeek V3.2 (verification, reasoning=16384)
                    │   └── Kimi K2.5 (verification, reasoning=1024)
                    │
                    ├── Tiered Consensus Resolution
                    │   ├── Tier 0: Unanimous (no API call)
                    │   ├── Tier 1: Majority, non-critical (no API call)
                    │   ├── Tier 2: Majority, critical (no API call)
                    │   ├── Tier 3: 3-way split, non-critical → Haiku 4.5
                    │   └── Tier 4: 3-way split, critical → Sonnet 4.6
                    │
                    └── Per-Claim Extraction (Haiku 4.5 Batch API)
                        └── 6,718 claims from 3,193 cases
```
