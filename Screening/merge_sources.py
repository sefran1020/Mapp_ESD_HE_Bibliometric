#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""merge_sources.py — Merge bibliographic records from Scopus (RIS), WoS (RIS),
and ERIC (NBIB) into a single deduplicated CSV.

Deduplication strategy:
  Phase 1 – exact DOI matching
  Phase 2 – fuzzy title matching (rapidfuzz) with year-blocking and author/journal
             confirmation

For each duplicate group the richest record is kept as primary and missing fields
are filled from secondary sources.
"""
from __future__ import annotations

# ══════════════════════════════════════════════════════════════════════════════
# Section 1 — Imports and configuration
# ══════════════════════════════════════════════════════════════════════════════

import argparse
import csv
import glob as globmod
import html
import os
import re
import sys
from collections import defaultdict

from rapidfuzz import fuzz

# --- Default file names (relative to script directory) ---
DEFAULT_SCOPUS = "SCOPUS.ris"
DEFAULT_WOS = ["WOS.ris"]
DEFAULT_ERIC_PATTERN = "ERIC*.nbib"
DEFAULT_OUTPUT = "consolidado_merged.csv"
FUZZY_THRESHOLD_DEFAULT = 90
UNCERTAIN_RANGE = (85, 89)

# RIS tags that may appear more than once per record
MULTI_VALUE_TAGS = frozenset({"AU", "KW", "AD", "SN", "C3", "WE", "FU"})

# Regex for a standard RIS tag line: two-char tag, two spaces, dash, space
RIS_TAG_RE = re.compile(r"^([A-Z][A-Z0-9])\s\s-\s?(.*)$")

# Regex for section headers concatenated in WoS structured abstracts
_WOS_ABSTRACT_HEADERS_RE = re.compile(
    r"(?<=[a-z.)])("
    r"Background|Objectives?|Purpose|Aims?|Introduction|Context|Rationale|"
    r"Methods?|Methodology|Design|Setting|Participants|Subjects|Sample|"
    r"Procedure|Measures?|Instruments?|Data Sources|Analysis|Intervention|"
    r"Results?|Findings|Outcomes?|"
    r"Discussion|Conclusions?|Implications?|Limitations?|Significance|"
    r"Summary|Recommendations?"
    r")(?=[A-Z])"
)

# NBIB/MEDLINE tag regex: 2-4 uppercase chars, then spaces, dash, space
NBIB_TAG_RE = re.compile(r"^([A-Z][A-Z0-9]{0,3})\s+- (.*)$")

# NBIB tags that may appear more than once per record
NBIB_MULTI_VALUE_TAGS = frozenset({"AU", "OT", "ISSN", "PT"})

# Output CSV column order
CSV_COLUMNS = [
    "Authors", "Title", "Publication_Year", "Journal_Name",
    "Volume", "Issue", "Pages", "DOI", "Abstract", "Keywords",
    "Affiliations", "Publisher", "ISSN", "Language", "Document_Type",
    "URL", "Source_DB", "Merged_From", "Richness_Score",
    "Times_Cited", "Funding_Text", "Funding_Agency",
    "WoS_Accession", "WoS_Index", "Journal_ISO", "ERIC_ID",
]


# ══════════════════════════════════════════════════════════════════════════════
# Section 2 — Format repair & content filters
# ══════════════════════════════════════════════════════════════════════════════

def fix_spaced_html_entities(raw: str) -> str:
    """Fix HTML entities with inserted spaces: ``& eacute;`` → ``&eacute;``

    Scopus and WoS sometimes export accented characters as ``& eacute;``
    (with a space after ``&``).  This collapses the space so that the
    standard ``html.unescape()`` can decode them.
    """
    return re.sub(r"& ([a-zA-Z]{2,8});", r"&\1;", raw)


def decode_html_entities(raw: str) -> str:
    """Decode HTML entities (&quot; &amp; etc.) that WoS/Scopus sometimes inject."""
    raw = fix_spaced_html_entities(raw)
    return html.unescape(raw)


# Medical ESD terms — articles about Endoscopic Submucosal Dissection, NOT
# Education for Sustainable Development.  Used for title+abstract screening.
_MEDICAL_ESD_TERMS = re.compile(
    r"endoscopic submucosal dissection|endoscopic submucosal|"
    r"esophageal stenosis|esophageal stricture|esophageal cancer|"
    r"esophageal squamous|oesophageal|"
    r"gastric (cancer|carcinoma|tumor|tumour|neoplasm|lesion|adenocarcinoma)|"
    r"colorectal (cancer|carcinoma|tumor|tumour|neoplasm|lesion|adenocarcinoma)|"
    r"gastrointestinal (stromal|tumor|tumour|neoplasm|lesion)|"
    r"submucosal (dissection|tumor|tumour)|"
    r"endoscopic (resection|mucosal|dissection)|"
    r"colonoscop|"
    r"rectal (cancer|carcinoma|tumor|tumour|neoplasm)|"
    r"duodenal (cancer|neoplasm|tumor|adenoma)|"
    r"mucosal defect|mucosal resection",
    re.IGNORECASE,
)


def _is_medical_esd(rec: dict) -> bool:
    """True when a record is about medical ESD (endoscopic), not educational ESD."""
    text = (rec.get("title", "") + " " + rec.get("abstract", "")).lower()
    return bool(_MEDICAL_ESD_TERMS.search(text))


def fix_wos_concatenation(raw: str) -> str:
    """Insert newlines before RIS tags that appear mid-line in WoS exports.

    WoS sometimes concatenates fields on a single line, e.g.::

        AD  - Wayne State Univ...USAC3  - Wayne State UniversityPU  - IEEE

    This inserts ``\\n`` before each ``XX  - `` tag that follows other content
    on the same line.
    """
    return re.sub(r"([^\n])([A-Z][A-Z0-9]  - )", r"\1\n\2", raw)


def fix_wos_abstract_headers(abstract: str) -> str:
    """Insert ': ' between section headers and text in WoS structured abstracts.

    WoS sometimes concatenates structured-abstract sections, e.g.::

        BackgroundArtificial intelligence...ResultsThe analysis...

    This inserts ``': '`` after each header to produce::

        Background: Artificial intelligence...Results: The analysis...
    """
    if not abstract:
        return abstract
    return _WOS_ABSTRACT_HEADERS_RE.sub(r" \1: ", abstract)


# ══════════════════════════════════════════════════════════════════════════════
# Section 3 — Generic RIS parser (Scopus + WoS)
# ══════════════════════════════════════════════════════════════════════════════

def parse_ris(text: str) -> list:
    """Parse RIS-formatted text into a list of ``{tag: value}`` dicts.

    * Multi-value tags (AU, KW, AD, SN, C3) → collected into **lists**.
    * Continuation lines (no tag prefix) → appended to previous tag value.
    * ``ER`` terminates a record; ``TY`` starts one.
    """
    records = []
    current: dict = {}
    current_tag: str | None = None

    for line in text.splitlines():
        stripped = line.rstrip()
        if not stripped:
            continue

        m = RIS_TAG_RE.match(stripped)
        if m:
            tag, value = m.group(1), m.group(2).strip()
            if tag == "TY":
                current = {"TY": value}
                current_tag = "TY"
            elif tag == "ER":
                if current:
                    records.append(current)
                current = {}
                current_tag = None
            else:
                if tag in MULTI_VALUE_TAGS:
                    current.setdefault(tag, []).append(value)
                else:
                    # If the tag already exists, append (rare duplicate tags)
                    if tag in current:
                        current[tag] = current[tag] + " " + value
                    else:
                        current[tag] = value
                current_tag = tag
        else:
            # Continuation line — append to previous tag
            if current_tag and current:
                val = stripped.strip()
                if not val:
                    continue
                if current_tag in MULTI_VALUE_TAGS:
                    lst = current.get(current_tag, [])
                    if lst:
                        lst[-1] += " " + val
                    else:
                        current.setdefault(current_tag, []).append(val)
                else:
                    current[current_tag] = current.get(current_tag, "") + "\n" + val

    # File may lack a final ER tag
    if current:
        records.append(current)
    return records


# ══════════════════════════════════════════════════════════════════════════════
# Section 4 — NBIB/MEDLINE parser (ERIC)
# ══════════════════════════════════════════════════════════════════════════════

def parse_nbib(text: str) -> list:
    """Parse NBIB (MEDLINE/PubMed) formatted text into a list of dicts.

    * Records are separated by blank lines.
    * Tags are 2-4 uppercase chars followed by ``  - value``.
    * Multi-value tags (AU, OT, ISSN, PT) → collected into **lists**.
    * Continuation lines (leading whitespace, no tag) → appended to previous value.
    """
    records = []
    current: dict = {}
    current_tag: str | None = None

    for line in text.splitlines():
        stripped = line.rstrip()

        # Blank line → end of record
        if not stripped:
            if current:
                records.append(current)
                current = {}
                current_tag = None
            continue

        m = NBIB_TAG_RE.match(stripped)
        if m:
            tag, value = m.group(1), m.group(2).strip()
            if tag in NBIB_MULTI_VALUE_TAGS:
                current.setdefault(tag, []).append(value)
            else:
                if tag in current:
                    current[tag] = current[tag] + " " + value
                else:
                    current[tag] = value
            current_tag = tag
        else:
            # Continuation line — append to previous tag
            val = stripped.strip()
            if current_tag and current and val:
                if current_tag in NBIB_MULTI_VALUE_TAGS:
                    lst = current.get(current_tag, [])
                    if lst:
                        lst[-1] += " " + val
                else:
                    current[current_tag] = current.get(current_tag, "") + " " + val

    # Last record if file does not end with a blank line
    if current:
        records.append(current)
    return records


# ══════════════════════════════════════════════════════════════════════════════
# Section 5 — Normalizers  (per-source → common schema)
# ══════════════════════════════════════════════════════════════════════════════

def normalize_doi(doi: str) -> str:
    """Lower-case, strip URL prefixes and whitespace."""
    if not doi:
        return ""
    doi = doi.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/",
                    "https://dx.doi.org/", "http://dx.doi.org/", "doi:"):
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    return doi.strip()


def _first_author_surname(authors: list) -> str:
    """Return the lower-cased surname of the first author."""
    if not authors:
        return ""
    first = authors[0].strip()
    if "," in first:
        return first.split(",")[0].strip().lower()
    parts = first.split()
    return parts[-1].strip().lower() if parts else ""


def _parse_pages(sp: str, ep: str, c7: str = "") -> str:
    if sp and ep:
        return f"{sp}-{ep}"
    if sp:
        return sp
    return c7


def _parse_times_cited_scopus(n1: str) -> str:
    if not n1:
        return ""
    m = re.search(r"Cited By:\s*(\d+)", n1)
    return m.group(1) if m else ""


def _parse_times_cited_wos(n1: str) -> str:
    if not n1:
        return ""
    m = re.search(r"Times Cited in Web of Science Core Collection:\s*(\d+)", n1)
    if m:
        return m.group(1)
    m = re.search(r"Total Times Cited:\s*(\d+)", n1)
    return m.group(1) if m else ""


def _clean_issn(val: str) -> str:
    """Strip trailing noise like ' (ISSN)' from Scopus SN values."""
    if not val:
        return ""
    return re.sub(r"\s*\(ISSN\)\s*$", "", val, flags=re.IGNORECASE).strip()


def _clean_title(title: str) -> str:
    """Strip trailing period and normalize internal whitespace."""
    if not title:
        return ""
    title = re.sub(r"\s+", " ", title).strip()
    if title.endswith("."):
        title = title[:-1]
    return title


def _clean_abstract(abstract: str) -> str:
    """Collapse newlines and normalize whitespace in abstract text.

    RIS continuation lines introduce ``\\n`` characters that create
    multi-line CSV fields, breaking parsers when combined with embedded
    quotes or semicolons.
    """
    if not abstract:
        return ""
    return re.sub(r"\s+", " ", abstract).strip()


_ERIC_SO_RE = re.compile(
    r"v(?P<vol>\d+)\s+n(?P<iss>\d+)\s+p(?P<pages>\S+)", re.IGNORECASE
)


def _parse_eric_so(so: str) -> dict:
    """Extract volume, issue, and pages from ERIC SO field as fallback.

    Format example: ``'v35 n2 p153-159 2025'``
    Returns dict with keys ``volume``, ``issue``, ``pages`` (empty strings if
    not matched).
    """
    result = {"volume": "", "issue": "", "pages": ""}
    if not so:
        return result
    m = _ERIC_SO_RE.search(so)
    if m:
        result["volume"] = m.group("vol")
        result["issue"] = m.group("iss")
        result["pages"] = m.group("pages")
    return result


# ── Scopus ────────────────────────────────────────────────────────────────────

def normalize_scopus(rec: dict) -> dict:
    authors = rec.get("AU", [])
    issn_list = rec.get("SN", [])
    return {
        "title":            _clean_title(rec.get("TI", "")),
        "authors":          list(authors),
        "publication_year": rec.get("PY", "").strip(),
        "abstract":         _clean_abstract(rec.get("AB", "")),
        "doi":              normalize_doi(rec.get("DO", "")),
        "keywords":         list(rec.get("KW", [])),
        "journal_name":     rec.get("T2", "").strip(),
        "volume":           rec.get("VL", "").strip(),
        "issue":            rec.get("IS", "").strip(),
        "pages":            _parse_pages(rec.get("SP", "").strip(),
                                         rec.get("EP", "").strip(),
                                         rec.get("C7", "").strip()),
        "affiliations":     list(rec.get("AD", [])),
        "publisher":        rec.get("PB", "").strip(),
        "funding_text":     "",
        "funding_agency":   "",
        "times_cited":      _parse_times_cited_scopus(rec.get("N1", "")),
        "wos_accession":    "",
        "wos_index":        "",
        "url":              rec.get("UR", "").strip(),
        "issn":             _clean_issn(issn_list[0]) if issn_list else "",
        "language":         rec.get("LA", "").strip(),
        "doc_type":         rec.get("M3", rec.get("TY", "")).strip(),
        "journal_iso":      "",
        "source_db":        "Scopus",
    }


# ── WoS ──────────────────────────────────────────────────────────────────────

def normalize_wos(rec: dict) -> dict:
    authors = rec.get("AU", [])
    affiliations = list(rec.get("AD", [])) + list(rec.get("C3", []))
    issn_list = rec.get("SN", [])
    fu_list = rec.get("FU", [])
    return {
        "title":            _clean_title(rec.get("TI", "")),
        "authors":          list(authors),
        "publication_year": rec.get("PY", "").strip(),
        "abstract":         _clean_abstract(fix_wos_abstract_headers(rec.get("AB", ""))),
        "doi":              normalize_doi(rec.get("DO", "")),
        "keywords":         list(rec.get("KW", [])),
        "journal_name":     rec.get("T2", "").strip(),
        "volume":           rec.get("VL", "").strip(),
        "issue":            rec.get("IS", "").strip(),
        "pages":            _parse_pages(rec.get("SP", "").strip(),
                                         rec.get("EP", "").strip(),
                                         rec.get("C7", "").strip()),
        "affiliations":     affiliations,
        "publisher":        rec.get("PU", "").strip(),
        "funding_text":     rec.get("FX", "").strip(),
        "funding_agency":   "; ".join(fu_list) if isinstance(fu_list, list) else str(fu_list).strip(),
        "times_cited":      _parse_times_cited_wos(rec.get("N1", "")),
        "wos_accession":    rec.get("AN", "").strip(),
        "wos_index":        "; ".join(rec.get("WE", [])),
        "url":              "",
        "issn":             _clean_issn(issn_list[0]) if issn_list else "",
        "language":         rec.get("LA", "").strip(),
        "doc_type":         rec.get("TY", "").strip(),
        "journal_iso":      rec.get("JI", "").strip(),
        "source_db":        "WoS",
    }


# ── ERIC ─────────────────────────────────────────────────────────────────────

def _parse_eric_year(dp: str) -> str:
    """Extract a 4-digit year from ERIC DP field (e.g. 'May 2021', '2025')."""
    if not dp:
        return ""
    m = re.search(r"\b(\d{4})\b", dp)
    return m.group(1) if m else ""


def _clean_eric_issn(val: str) -> str:
    """Strip 'ISSN-' or 'EISSN-' prefixes from ERIC ISSN values."""
    if not val:
        return ""
    return re.sub(r"^[E]?ISSN-", "", val, flags=re.IGNORECASE).strip()


def normalize_eric(rec: dict) -> dict:
    authors = rec.get("AU", [])
    keywords = rec.get("OT", [])
    issn_list = rec.get("ISSN", [])
    pt_list = rec.get("PT", [])

    volume = rec.get("VI", "").strip()
    issue = rec.get("IP", "").strip()
    pages = rec.get("PG", "").strip()
    # Fallback: extract vol/issue/pages from SO field if primary fields empty
    if not volume or not issue or not pages:
        so_parsed = _parse_eric_so(rec.get("SO", ""))
        if not volume:
            volume = so_parsed["volume"]
        if not issue:
            issue = so_parsed["issue"]
        if not pages:
            pages = so_parsed["pages"]

    return {
        "title":            _clean_title(rec.get("TI", "")),
        "authors":          list(authors),
        "publication_year": _parse_eric_year(rec.get("DP", "")),
        "abstract":         _clean_abstract(rec.get("AB", "")),
        "doi":              normalize_doi(rec.get("AID", "")),
        "keywords":         list(keywords),
        "journal_name":     rec.get("JT", "").strip(),
        "volume":           volume,
        "issue":            issue,
        "pages":            pages,
        "affiliations":     [],
        "publisher":        "",
        "funding_text":     "",
        "funding_agency":   "",
        "times_cited":      "",
        "wos_accession":    "",
        "wos_index":        "",
        "url":              rec.get("LID", "").strip(),
        "issn":             _clean_eric_issn(issn_list[0]) if issn_list else "",
        "language":         rec.get("LA", "").strip(),
        "doc_type":         pt_list[0].strip() if pt_list else "",
        "journal_iso":      "",
        "source_db":        "ERIC",
        "eric_id":          rec.get("OID", "").strip(),
    }


# ── Quality filters ─────────────────────────────────────────────────────────

def _has_required_pre_dedup(rec: dict) -> bool:
    """Require title AND at least one author (pre-dedup filter)."""
    return bool(rec.get("title", "").strip()) and bool(rec.get("authors"))


def _has_abstract(rec: dict) -> bool:
    """Require non-empty abstract (post-merge filter)."""
    return bool(rec.get("abstract", "").strip())


# ══════════════════════════════════════════════════════════════════════════════
# Section 6 — Deduplication engine
# ══════════════════════════════════════════════════════════════════════════════

class _UnionFind:
    """Disjoint-set with path compression and union by rank."""

    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


def _normalize_title_for_compare(t: str) -> str:
    t = t.lower().strip()
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def deduplicate(records: list, fuzzy_threshold: int = 90):
    """Two-phase deduplication: exact DOI then fuzzy title.

    Returns
    -------
    groups : list[list[int]]
        Each inner list holds indices of records that are duplicates.
    uncertain : list[tuple[int,int,float]]
        Pairs with scores in the uncertain range for manual review.
    stats : dict
    """
    n = len(records)
    uf = _UnionFind(n)
    doi_matches = 0
    title_matches = 0
    uncertain = []

    # ── Phase 1: DOI exact match ──────────────────────────────────────────
    doi_index: dict[str, list[int]] = defaultdict(list)
    for i, rec in enumerate(records):
        d = rec["doi"]
        if d:
            doi_index[d].append(i)

    for indices in doi_index.values():
        if len(indices) > 1:
            for j in range(1, len(indices)):
                if uf.union(indices[0], indices[j]):
                    doi_matches += 1

    # ── Phase 2: fuzzy title match (year-blocking ±1) ─────────────────────
    year_index: dict[int, list[int]] = defaultdict(list)
    for i, rec in enumerate(records):
        try:
            y = int(rec["publication_year"])
        except (ValueError, TypeError):
            y = 0
        year_index[y].append(i)

    # Pre-compute helpers
    norm_titles = [_normalize_title_for_compare(r.get("title", "")) for r in records]
    first_authors = [_first_author_surname(r.get("authors", [])) for r in records]
    norm_journals = [r.get("journal_name", "").lower().strip() for r in records]

    for y, indices_in_year in year_index.items():
        # Candidates: records from years y-1, y, y+1
        candidate_set: list[int] = []
        for dy in (y - 1, y, y + 1):
            candidate_set.extend(year_index.get(dy, []))

        for i in indices_in_year:
            if not norm_titles[i]:
                continue
            for j in candidate_set:
                if j <= i:
                    continue
                if uf.find(i) == uf.find(j):
                    continue
                if not norm_titles[j]:
                    continue

                score = fuzz.token_sort_ratio(norm_titles[i], norm_titles[j])

                if score >= fuzzy_threshold:
                    # Require author OR journal confirmation
                    author_ok = (first_authors[i] and first_authors[j]
                                 and first_authors[i] == first_authors[j])
                    journal_ok = (norm_journals[i] and norm_journals[j]
                                  and fuzz.token_sort_ratio(
                                      norm_journals[i], norm_journals[j]) >= 80)
                    if author_ok or journal_ok or score >= 95:
                        uf.union(i, j)
                        title_matches += 1

                elif UNCERTAIN_RANGE[0] <= score <= UNCERTAIN_RANGE[1]:
                    author_ok = (first_authors[i] and first_authors[j]
                                 and first_authors[i] == first_authors[j])
                    journal_ok = (norm_journals[i] and norm_journals[j]
                                  and fuzz.token_sort_ratio(
                                      norm_journals[i], norm_journals[j]) >= 80)
                    if author_ok or journal_ok:
                        uncertain.append((i, j, score))

    # ── Build groups ──────────────────────────────────────────────────────
    groups_map: dict[int, list[int]] = defaultdict(list)
    for i in range(n):
        groups_map[uf.find(i)].append(i)
    groups = list(groups_map.values())

    stats = {
        "total_input": n,
        "doi_matches": doi_matches,
        "title_matches": title_matches,
        "unique_after_dedup": len(groups),
        "uncertain_pairs": len(uncertain),
    }
    return groups, uncertain, stats


# ══════════════════════════════════════════════════════════════════════════════
# Section 7 — Richness scoring
# ══════════════════════════════════════════════════════════════════════════════

def compute_richness(rec: dict) -> int:
    """Score a record's metadata completeness (max ≈105)."""
    s = 0

    # Abstract (up to 15 pts — 1 per 10 words)
    abstract = rec.get("abstract", "")
    if abstract:
        s += min(15, len(abstract.split()) // 10)

    # DOI: 15 pts
    if rec.get("doi"):
        s += 15

    # Keywords: up to 10 pts
    s += min(10, len(rec.get("keywords", [])))

    # Authors: up to 10 pts
    s += min(10, len(rec.get("authors", [])))

    # Title: 10 pts
    if rec.get("title"):
        s += 10

    # Year: 5 pts
    if rec.get("publication_year"):
        s += 5

    # Journal: 5 pts
    if rec.get("journal_name"):
        s += 5

    # Volume / Issue / Pages / ISSN: 3 pts each
    for field in ("volume", "issue", "pages", "issn"):
        if rec.get(field):
            s += 3

    # Affiliations: up to 8 pts (2 per affiliation)
    s += min(8, len(rec.get("affiliations", [])) * 2)

    # Publisher: 2 pts
    if rec.get("publisher"):
        s += 2

    # Funding text: 3 pts
    if rec.get("funding_text"):
        s += 3

    # WoS accession: 2 pts
    if rec.get("wos_accession"):
        s += 2

    # Times cited: 3 pts
    if rec.get("times_cited"):
        s += 3

    # URL: 2 pts
    if rec.get("url"):
        s += 2

    # Language: 2 pts
    if rec.get("language"):
        s += 2

    # Document type: 2 pts
    if rec.get("doc_type"):
        s += 2

    return s


# ══════════════════════════════════════════════════════════════════════════════
# Section 8 — Complementary merge
# ══════════════════════════════════════════════════════════════════════════════

def _is_allcaps(s: str) -> bool:
    """True when a string is predominantly UPPER-CASE (ignoring non-alpha)."""
    alpha = [c for c in s if c.isalpha()]
    if len(alpha) < 4:
        return False
    return sum(c.isupper() for c in alpha) / len(alpha) > 0.80


def _avg_author_name_len(authors: list) -> float:
    """Average character-length of author names — proxy for name completeness.

    IEEE gives full first names (``Pu, Ning``  → 8 chars) while WoS/Scopus
    abbreviate (``Pu, N`` → 4 chars).  A higher average means fuller names.
    """
    if not authors:
        return 0.0
    return sum(len(a) for a in authors) / len(authors)


def merge_group(all_records: list, group_indices: list) -> dict:
    """Merge a duplicate group ensuring the **most complete** metadata.

    Strategy per field:

    * **authors** → list with highest average name length (full names > initials),
      among lists with the same number of authors as the longest list.
    * **journal_name** → prefer proper-case over ALL-CAPS; then longest.
    * **title** → prefer proper-case over ALL-CAPS; then longest.
    * **abstract** → longest text.
    * **keywords** → union of all sources (case-insensitive dedup).
    * **affiliations** → union of all sources.
    * **times_cited** → maximum value.
    * **pages** → prefer a range like ``648-661`` over an article number.
    * Everything else → fill blanks from secondaries.
    """
    # Build working copies sorted by richness desc
    group = []
    for idx in group_indices:
        r = {}
        for k, v in all_records[idx].items():
            r[k] = list(v) if isinstance(v, list) else v
        group.append(r)
    group.sort(key=lambda r: r.get("richness_score", 0), reverse=True)

    primary = group[0]
    source_dbs = {primary["source_db"]}

    # ── Pre-scan: pick best authors / journal / title across all copies ───

    # Authors: among lists tied for most authors, prefer the one with the
    # longest average name (full first names vs initials).
    best_authors = primary.get("authors", [])
    best_author_count = len(best_authors)
    best_author_avg = _avg_author_name_len(best_authors)
    for rec in group[1:]:
        au = rec.get("authors", [])
        n = len(au)
        avg = _avg_author_name_len(au)
        # Prefer more authors; on tie prefer fuller names
        if n > best_author_count or (n == best_author_count and avg > best_author_avg):
            best_authors = au
            best_author_count = n
            best_author_avg = avg
    primary["authors"] = list(best_authors)

    # Journal name: prefer proper-case, then longest
    best_journal = primary.get("journal_name", "")
    for rec in group[1:]:
        jn = rec.get("journal_name", "")
        if not jn:
            continue
        if not best_journal:
            best_journal = jn
            continue
        # If current best is ALL-CAPS and candidate is not → switch
        if _is_allcaps(best_journal) and not _is_allcaps(jn):
            best_journal = jn
        # Among same-case entries, prefer longer
        elif _is_allcaps(best_journal) == _is_allcaps(jn) and len(jn) > len(best_journal):
            best_journal = jn
    primary["journal_name"] = best_journal

    # Title: prefer proper-case, then longest
    best_title = primary.get("title", "")
    for rec in group[1:]:
        t = rec.get("title", "")
        if not t:
            continue
        if not best_title:
            best_title = t
            continue
        if _is_allcaps(best_title) and not _is_allcaps(t):
            best_title = t
        elif _is_allcaps(best_title) == _is_allcaps(t) and len(t) > len(best_title):
            best_title = t
    primary["title"] = best_title

    # Pages: prefer a range (contains "-") over a bare article number
    best_pages = primary.get("pages", "")
    for rec in group[1:]:
        pg = rec.get("pages", "")
        if not pg:
            continue
        if not best_pages:
            best_pages = pg
            continue
        if "-" not in best_pages and "-" in pg:
            best_pages = pg
    primary["pages"] = best_pages

    # ── Field-by-field complementary merge ────────────────────────────────

    for secondary in group[1:]:
        source_dbs.add(secondary["source_db"])
        for key, sec_val in secondary.items():
            if key in ("source_db", "richness_score",
                       "authors", "journal_name", "title", "pages"):
                continue  # already handled above
            pri_val = primary.get(key)

            # keywords → union (case-insensitive dedup)
            if key == "keywords":
                if sec_val:
                    existing = {k.lower() for k in (pri_val or [])}
                    for kw in sec_val:
                        if kw.lower() not in existing:
                            primary.setdefault("keywords", []).append(kw)
                            existing.add(kw.lower())
                continue

            # abstract → keep longest
            if key == "abstract":
                if sec_val and len(sec_val) > len(pri_val or ""):
                    primary["abstract"] = sec_val
                continue

            # times_cited → keep max
            if key == "times_cited":
                try:
                    s = int(sec_val) if sec_val else 0
                    p = int(pri_val) if pri_val else 0
                    if s > p:
                        primary["times_cited"] = str(s)
                except (ValueError, TypeError):
                    pass
                continue

            # affiliations → union
            if key == "affiliations":
                if sec_val:
                    existing = {a.lower() for a in (pri_val or [])}
                    for aff in sec_val:
                        if aff.lower() not in existing:
                            primary.setdefault("affiliations", []).append(aff)
                            existing.add(aff.lower())
                continue

            # default → fill if primary is empty
            if isinstance(pri_val, list):
                if not pri_val and sec_val:
                    primary[key] = list(sec_val) if isinstance(sec_val, list) else sec_val
            else:
                if not pri_val and sec_val:
                    primary[key] = sec_val

    primary["merged_from"] = "+".join(sorted(source_dbs))
    return primary


# ══════════════════════════════════════════════════════════════════════════════
# Section 9 — Export (CSV, report, uncertain)
# ══════════════════════════════════════════════════════════════════════════════

def _join(lst):
    """Join a list with '; ' for CSV serialization."""
    if not lst:
        return ""
    return "; ".join(str(x) for x in lst)


def _to_csv_row(rec: dict) -> dict:
    return {
        "Authors":          _join(rec.get("authors", [])),
        "Title":            rec.get("title", ""),
        "Publication_Year": rec.get("publication_year", ""),
        "Journal_Name":     rec.get("journal_name", ""),
        "Volume":           rec.get("volume", ""),
        "Issue":            rec.get("issue", ""),
        "Pages":            rec.get("pages", ""),
        "DOI":              rec.get("doi", ""),
        "Abstract":         rec.get("abstract", ""),
        "Keywords":         _join(rec.get("keywords", [])),
        "Affiliations":     _join(rec.get("affiliations", [])),
        "Publisher":        rec.get("publisher", ""),
        "ISSN":             rec.get("issn", ""),
        "Language":         rec.get("language", ""),
        "Document_Type":    rec.get("doc_type", ""),
        "URL":              rec.get("url", ""),
        "Source_DB":        rec.get("source_db", ""),
        "Merged_From":      rec.get("merged_from", rec.get("source_db", "")),
        "Richness_Score":   str(rec.get("richness_score", 0)),
        "Times_Cited":      rec.get("times_cited", ""),
        "Funding_Text":     rec.get("funding_text", ""),
        "Funding_Agency":   rec.get("funding_agency", ""),
        "WoS_Accession":    rec.get("wos_accession", ""),
        "WoS_Index":        rec.get("wos_index", ""),
        "Journal_ISO":      rec.get("journal_iso", ""),
        "ERIC_ID":          rec.get("eric_id", ""),
    }


def export_csv(records: list, output_path: str):
    with open(output_path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS,
                                delimiter=";", quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for rec in records:
            writer.writerow(_to_csv_row(rec))


def write_report(stats: dict, source_counts: dict, overlap: dict,
                 merged_from_counts: dict, top_groups: list,
                 output_dir: str, *,
                 filter_stats: dict | None = None,
                 completeness: dict | None = None,
                 retracted: list | None = None) -> str:
    path = os.path.join(output_dir, "dedup_report.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("  DEDUPLICATION REPORT\n")
        f.write("=" * 60 + "\n\n")

        f.write("--- Records per source (raw parsed) ---\n")
        raw_total = sum(source_counts.get(s, 0) for s in ("Scopus", "WoS", "ERIC"))
        for src in ("Scopus", "WoS", "ERIC"):
            f.write(f"  {src:8s}: {source_counts.get(src, 0):>6,}\n")
        f.write(f"  {'TOTAL':8s}: {raw_total:>6,}\n\n")

        # ── Quality filtering stats ──────────────────────────────────────
        if filter_stats:
            f.write("--- Quality filtering (pre-dedup) ---\n")
            f.write("  Removed records missing title or authors:\n")
            pre = filter_stats.get("pre_dedup", {})
            pre_total = 0
            for src in ("Scopus", "WoS", "ERIC"):
                cnt = pre.get(src, 0)
                pre_total += cnt
                if cnt:
                    f.write(f"    {src:8s}: {cnt:>5,}\n")
            f.write(f"    {'TOTAL':8s}: {pre_total:>5,}\n\n")

            med = filter_stats.get("medical_esd", {})
            med_total = sum(med.values()) if med else 0
            if med_total:
                f.write("--- Content filter (medical ESD — endoscopic) ---\n")
                for src in ("Scopus", "WoS", "ERIC"):
                    cnt = med.get(src, 0)
                    if cnt:
                        f.write(f"    {src:8s}: {cnt:>5,}\n")
                f.write(f"    {'TOTAL':8s}: {med_total:>5,}\n\n")

            f.write(f"  Into dedup:  {stats['total_input']:>6,}\n\n")

            f.write("--- Quality filtering (post-merge) ---\n")
            f.write("  Removed records without abstract:\n")
            post = filter_stats.get("post_merge", {})
            post_total = sum(post.values()) if post else 0
            if post:
                for src, cnt in sorted(post.items()):
                    if cnt:
                        f.write(f"    {src:24s}: {cnt:>5,}\n")
            f.write(f"    {'TOTAL':24s}: {post_total:>5,}\n\n")

        f.write("--- Deduplication results ---\n")
        f.write(f"  DOI-based matches:      {stats['doi_matches']:>5,}\n")
        f.write(f"  Title-fuzzy matches:    {stats['title_matches']:>5,}\n")
        removed = stats["total_input"] - stats["unique_after_dedup"]
        f.write(f"  Duplicates removed:     {removed:>5,}\n")
        f.write(f"  Unique records:         {stats['unique_after_dedup']:>5,}\n")
        f.write(f"  Uncertain pairs:        {stats['uncertain_pairs']:>5,}\n\n")

        f.write("--- Records per source (after dedup) ---\n")
        for combo, cnt in sorted(merged_from_counts.items()):
            f.write(f"  {combo:24s}: {cnt:>5,}\n")
        f.write("\n")

        f.write("--- Overlap between source pairs ---\n")
        for pair, count in sorted(overlap.items()):
            f.write(f"  {pair:16s}: {count:>5,} shared records\n")
        f.write("\n")

        f.write("--- Top 10 largest duplicate groups ---\n")
        for i, (size, title, sources) in enumerate(top_groups[:10], 1):
            f.write(f"  {i:2d}. [{size} recs] {sources:20s} | {title[:70]}\n")
        f.write("\n")

        # ── Metadata completeness ────────────────────────────────────────
        if completeness:
            f.write("--- Metadata completeness (final export) ---\n")
            for field, pct in completeness.items():
                bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
                f.write(f"  {field:18s}: {pct:5.1f}%  [{bar}]\n")
            f.write("\n")

        # ── Retracted articles warning ───────────────────────────────────
        if retracted:
            f.write(f"--- WARNING: {len(retracted)} retracted article(s) detected ---\n")
            for rec in retracted:
                f.write(f"  - {rec.get('title', '?')[:70]}\n")
                f.write(f"    DOI: {rec.get('doi', 'N/A')}  Source: {rec.get('source_db', '?')}\n")
            f.write("\n")

    return path


def write_uncertain(pairs: list, records: list, output_dir: str) -> str:
    path = os.path.join(output_dir, "uncertain_duplicates.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh, delimiter=";")
        writer.writerow(["Score", "Title_A", "Source_A", "DOI_A",
                         "Title_B", "Source_B", "DOI_B",
                         "Author1_A", "Author1_B"])
        for idx_a, idx_b, score in pairs:
            a, b = records[idx_a], records[idx_b]
            writer.writerow([
                f"{score:.1f}",
                a.get("title", ""), a.get("source_db", ""), a.get("doi", ""),
                b.get("title", ""), b.get("source_db", ""), b.get("doi", ""),
                _first_author_surname(a.get("authors", [])),
                _first_author_surname(b.get("authors", [])),
            ])
    return path


# ══════════════════════════════════════════════════════════════════════════════
# Section 10 — main()
# ══════════════════════════════════════════════════════════════════════════════

def _read_file(path: str) -> str:
    """Read text trying utf-8-sig → utf-8 → latin-1."""
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            with open(path, encoding=enc) as fh:
                return fh.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise RuntimeError(f"Cannot decode file: {path}")


def main():
    ap = argparse.ArgumentParser(
        description="Merge Scopus/WoS/ERIC bibliographic records into a "
                    "deduplicated CSV.")
    ap.add_argument("--scopus", default=DEFAULT_SCOPUS,
                    help="Scopus RIS file  (default: %(default)s)")
    ap.add_argument("--wos", nargs="+", default=DEFAULT_WOS,
                    help="WoS RIS file(s)  (default: %(default)s)")
    ap.add_argument("--eric-pattern", default=DEFAULT_ERIC_PATTERN,
                    help="Glob pattern for ERIC NBIB files  (default: %(default)s)")
    ap.add_argument("--output", default=DEFAULT_OUTPUT,
                    help="Output CSV path  (default: %(default)s)")
    ap.add_argument("--fuzzy-threshold", type=int, default=FUZZY_THRESHOLD_DEFAULT,
                    help="Fuzzy title threshold 0-100  (default: %(default)s)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Parse and report counts; do not deduplicate or write CSV")
    args = ap.parse_args()

    base = os.path.dirname(os.path.abspath(__file__))

    def resolve(p):
        return p if os.path.isabs(p) else os.path.join(base, p)

    scopus_path = resolve(args.scopus)
    wos_paths = [resolve(p) for p in args.wos]
    eric_pattern = resolve(args.eric_pattern)
    output_path = resolve(args.output)
    output_dir = os.path.dirname(output_path) or base

    all_records: list[dict] = []
    source_counts: dict[str, int] = {}

    # ── 1. Scopus ─────────────────────────────────────────────────────────
    print(f"[1/3] Loading Scopus: {scopus_path}")
    raw = _read_file(scopus_path)
    raw = decode_html_entities(raw)
    scopus_parsed = parse_ris(raw)
    scopus_norm = [normalize_scopus(r) for r in scopus_parsed]
    source_counts["Scopus"] = len(scopus_norm)
    all_records.extend(scopus_norm)
    print(f"      -> {len(scopus_norm):,} records")

    # ── 2. WoS ────────────────────────────────────────────────────────────
    wos_total = 0
    for idx, wp in enumerate(wos_paths, 1):
        print(f"[2/3] Loading WoS ({idx}/{len(wos_paths)}): {wp}")
        raw = _read_file(wp)
        raw = fix_wos_concatenation(raw)
        raw = decode_html_entities(raw)
        wos_parsed = parse_ris(raw)
        wos_norm = [normalize_wos(r) for r in wos_parsed]
        wos_total += len(wos_norm)
        all_records.extend(wos_norm)
        print(f"      -> {len(wos_norm):,} records")
    source_counts["WoS"] = wos_total

    # ── 3. ERIC ────────────────────────────────────────────────────────────
    eric_files = sorted(globmod.glob(eric_pattern))
    if not eric_files:
        print(f"[3/3] WARNING: no ERIC files matching {eric_pattern}")
        source_counts["ERIC"] = 0
    else:
        print(f"[3/3] Loading ERIC: {len(eric_files)} file(s)")
        eric_total = 0
        for nbib_path in eric_files:
            raw = _read_file(nbib_path)
            raw = decode_html_entities(raw)
            entries = parse_nbib(raw)
            eric_norm = [normalize_eric(e) for e in entries]
            eric_total += len(eric_norm)
            all_records.extend(eric_norm)
        source_counts["ERIC"] = eric_total
        print(f"      -> {eric_total:,} records total")

    total = len(all_records)
    print(f"\nTotal raw records: {total:,}")

    # ── Pre-dedup quality filter (require title + author) ────────────────
    filter_stats: dict = {"pre_dedup": {}, "post_merge": {}}
    pre_dedup_removed: dict[str, int] = defaultdict(int)
    kept: list[dict] = []
    for rec in all_records:
        if _has_required_pre_dedup(rec):
            kept.append(rec)
        else:
            pre_dedup_removed[rec["source_db"]] += 1
    if sum(pre_dedup_removed.values()):
        print(f"\nPre-dedup filter (no title or no authors): removed {sum(pre_dedup_removed.values()):,}")
        for src, cnt in sorted(pre_dedup_removed.items()):
            print(f"  {src}: {cnt:,}")
    filter_stats["pre_dedup"] = dict(pre_dedup_removed)
    all_records = kept

    # ── Content filter: remove medical ESD (endoscopic) articles ───────
    medical_removed: dict[str, int] = defaultdict(int)
    kept2: list[dict] = []
    for rec in all_records:
        if _is_medical_esd(rec):
            medical_removed[rec["source_db"]] += 1
        else:
            kept2.append(rec)
    if sum(medical_removed.values()):
        print(f"\nContent filter (medical ESD — endoscopic): removed {sum(medical_removed.values()):,}")
        for src, cnt in sorted(medical_removed.items()):
            print(f"  {src}: {cnt:,}")
    filter_stats["medical_esd"] = dict(medical_removed)
    all_records = kept2

    # ── Richness scores ───────────────────────────────────────────────────
    print("Computing richness scores ...")
    for rec in all_records:
        rec["richness_score"] = compute_richness(rec)

    if args.dry_run:
        print("\n[DRY-RUN] Parsing complete — skipping dedup & export.")
        for src, cnt in sorted(source_counts.items()):
            print(f"  {src}: {cnt:,}")
        print(f"  After pre-dedup filter: {len(all_records):,}")
        return

    # ── Deduplication ─────────────────────────────────────────────────────
    print("Deduplicating (this may take a minute) ...")
    groups, uncertain, stats = deduplicate(all_records, args.fuzzy_threshold)
    print(f"  DOI matches:   {stats['doi_matches']:,}")
    print(f"  Title matches: {stats['title_matches']:,}")
    print(f"  Unique:        {stats['unique_after_dedup']:,}")

    # ── Merge ─────────────────────────────────────────────────────────────
    print("Merging duplicate groups ...")
    merged: list[dict] = []
    for gidx in groups:
        if len(gidx) == 1:
            rec = {}
            for k, v in all_records[gidx[0]].items():
                rec[k] = list(v) if isinstance(v, list) else v
            rec["merged_from"] = rec["source_db"]
            merged.append(rec)
        else:
            merged.append(merge_group(all_records, gidx))

    # Recompute richness after complementary merge
    for rec in merged:
        rec["richness_score"] = compute_richness(rec)

    # ── Post-merge quality filter (require abstract) ─────────────────────
    post_merge_removed: dict[str, int] = defaultdict(int)
    kept_merged: list[dict] = []
    for rec in merged:
        if _has_abstract(rec):
            kept_merged.append(rec)
        else:
            post_merge_removed[rec.get("merged_from", rec["source_db"])] += 1
    if sum(post_merge_removed.values()):
        print(f"\nPost-merge filter (no abstract): removed {sum(post_merge_removed.values()):,}")
        for src, cnt in sorted(post_merge_removed.items()):
            print(f"  {src}: {cnt:,}")
    filter_stats["post_merge"] = dict(post_merge_removed)
    merged = kept_merged

    # Sort: richness desc, then title asc
    merged.sort(key=lambda r: (-r.get("richness_score", 0),
                                r.get("title", "").lower()))

    # ── Statistics ────────────────────────────────────────────────────────
    overlap: dict[str, int] = defaultdict(int)
    top_groups: list = []
    for gidx in groups:
        if len(gidx) <= 1:
            continue
        sources = sorted({all_records[i]["source_db"] for i in gidx})
        title = all_records[gidx[0]].get("title", "?")
        top_groups.append((len(gidx), title, "+".join(sources)))
        for a in range(len(sources)):
            for b in range(a + 1, len(sources)):
                overlap[f"{sources[a]}-{sources[b]}"] += 1
    top_groups.sort(key=lambda x: -x[0])

    merged_from_counts: dict[str, int] = defaultdict(int)
    for rec in merged:
        merged_from_counts[rec.get("merged_from", "?")] += 1

    # ── Metadata completeness ────────────────────────────────────────────
    completeness: dict[str, float] = {}
    n_final = len(merged)
    if n_final:
        comp_fields = {
            "Authors":    lambda r: bool(r.get("authors")),
            "Title":      lambda r: bool(r.get("title", "").strip()),
            "Year":       lambda r: bool(r.get("publication_year", "").strip()),
            "Abstract":   lambda r: bool(r.get("abstract", "").strip()),
            "DOI":        lambda r: bool(r.get("doi", "").strip()),
            "Journal":    lambda r: bool(r.get("journal_name", "").strip()),
            "Volume":     lambda r: bool(r.get("volume", "").strip()),
            "Issue":      lambda r: bool(r.get("issue", "").strip()),
            "Pages":      lambda r: bool(r.get("pages", "").strip()),
            "Keywords":   lambda r: bool(r.get("keywords")),
            "Affiliations": lambda r: bool(r.get("affiliations")),
            "ISSN":       lambda r: bool(r.get("issn", "").strip()),
            "Language":   lambda r: bool(r.get("language", "").strip()),
        }
        for field, test in comp_fields.items():
            completeness[field] = 100.0 * sum(1 for r in merged if test(r)) / n_final

    # ── Detect retracted articles ────────────────────────────────────────
    retracted = [r for r in merged
                 if "retract" in r.get("doc_type", "").lower()
                 or "retract" in r.get("title", "").lower()]
    if retracted:
        print(f"\nWARNING: {len(retracted)} retracted article(s) detected")

    # ── Export ────────────────────────────────────────────────────────────
    print(f"\nExporting {len(merged):,} records -> {output_path}")
    export_csv(merged, output_path)

    rpt = write_report(stats, source_counts, overlap, merged_from_counts,
                        top_groups, output_dir,
                        filter_stats=filter_stats,
                        completeness=completeness,
                        retracted=retracted)
    print(f"Report:     {rpt}")

    if uncertain:
        unc = write_uncertain(uncertain, all_records, output_dir)
        print(f"Uncertain:  {unc}")

    print("\nDone!")


if __name__ == "__main__":
    main()
