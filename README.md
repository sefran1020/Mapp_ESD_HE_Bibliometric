# Mapping the Intellectual Architecture of Education for Sustainable Development in Higher Education: A Bibliometric and AI-Assisted Thematic Synthesis

---

## Overview

This repository contains the **data, scripts, analyses, and manuscript materials** for a comprehensive bibliometric systematic review that exhaustively maps the field of **Education for Sustainable Development (ESD)** in higher education and vocational education and training (VET), covering the period **2015–2026**.

The study integrates three complementary methodological approaches:

1. **Bibliometric network analysis** (co-citation, bibliographic coupling, keyword co-occurrence, co-authorship)
2. **AI-assisted inductive thematic synthesis** (LLM processing with grounding verification)
3. **Systematic knowledge gap detection** (structural, declared, and emergent gaps)

### Final Analytical Corpus

| Metric | Value |
|--------|-------|
| Articles in final corpus | **442** |
| Temporal coverage | 2015–2026 |
| Databases queried | Scopus, Web of Science, ERIC |
| Initial records retrieved | 3,367 |
| Countries represented | 110+ |
| Cited references analyzed | 10,009 |
| Knowledge gaps identified | 40+ |
| Open access coverage | 50.45% |

---

## Research Question

**How has the integration of Education for Sustainable Development, climate literacy, green skills, and sustainability literacy been researched in higher education and vocational education contexts since the adoption of the 2030 Agenda, and what conceptual frameworks, pedagogical strategies, institutional approaches, and measurement instruments have been employed?**

### PICO Framework

- **P (Population):** Students, educators, institutions, and curricula within higher education (universities, tertiary institutions) and vocational education and training (VET) systems globally.
- **I (Intervention):** Integration of ESD, climate literacy, green skills, and sustainability literacy frameworks into curricula, pedagogical strategies, institutional policies, and competency frameworks.
- **C (Comparison):** Comparative analyses across institutional types, geographic regions, disciplinary fields, pre/post-SDG adoption periods, or between ESD-traditional and climate literacy-emergent approaches.
- **O (Outcome):** Development, integration, or assessment of sustainability-related competencies: ESD competencies, climate literacy, green skills, sustainability literacy, curriculum greening and institutional transformation, and pedagogical strategies.

---

## Repository Structure

```
paraRepositorioSp/
│
├── README.md                          ← This file
│
├── recoleccionBasesDatos/             ← Search strategy and data collection documentation
│   ├── propuestaRevision.txt          ← Review proposal with PICO framework and search string
│   ├── few_shot_examples.txt          ← Training examples for AI-assisted classification
│   └── ### Virtual Screening Team.txt ← Virtual screening team coordination protocol
│
├── Screening/                         ← Deduplication, screening, and corpus selection
│   ├── merge_sources.py               ← Python script for multi-source merging and deduplication
│   ├── consolidado.csv                ← Consolidated records pre-deduplication
│   ├── consolidado_merged.csv         ← Merged records post-deduplication (1,987 unique)
│   ├── consolidado2.csv               ← Intermediate consolidated file
│   ├── dedup_report.txt               ← Detailed deduplication report
│   ├── uncertain_duplicates.csv       ← Uncertain duplicate pairs for manual review
│   ├── errores.csv                    ← Records with parsing errors
│   ├── phase1_results.csv             ← Phase 1 screening results
│   ├── phase2_results.csv             ← Phase 2 screening results with PICO decisions
│   ├── reliability_metrics.csv        ← Inter-rater reliability metrics
│   ├── disagreement_report.csv        ← Reviewer disagreement report
│   ├── seleccionados80.csv            ← Final corpus (442 articles, threshold ≥80/100)
│   ├── criterios_metricas_screening.md     ← Detailed inclusion/exclusion criteria
│   ├── reliability_metrics_80.md           ← Final corpus reliability metrics
│   └── metricas_seleccionados_umbral80.md  ← Descriptive metrics for selected corpus
│
├── AnalisisDatos/                     ← Complete bibliometric and thematic analyses
│   ├── bibliometrix_export.csv        ← Complete bibliometric dataset (443 × 91 columns)
│   ├── bibliometrix_export.bib        ← BibTeX format export
│   ├── bibliometrix_analysis.R        ← R script (bibliometrix package) for full analysis
│   ├── citation_keys_mapping.txt      ← Citation key mapping
│   ├── citation_keys_mapping_full.txt ← Complete citation key mapping
│   │
│   ├── figures/                       ← Bibliometric visualizations (45+ PNG figures)
│   │   ├── lotka_author_productivity.png
│   │   ├── bradford_journals.png
│   │   ├── temporal_trends.png
│   │   ├── conceptual_structure_map.png
│   │   ├── country_collaboration.png
│   │   ├── keyword_frequency.png
│   │   ├── keyword_trends.png
│   │   ├── methods_by_year.png
│   │   ├── methods_by_country.png
│   │   ├── network_cocitation_cluster.png
│   │   ├── network_coauthorship_*.png
│   │   ├── network_bibliographic_coupling_*.png
│   │   ├── network_keyword_cooccurrence_*.png
│   │   └── by_item_type/              ← Stratified analysis by document type
│   │       ├── Book Chapter/
│   │       ├── conferencePaper/
│   │       └── journalArticle/
│   │
│   ├── networks/                      ← Network files in standard formats
│   │   ├── cocitation.{gexf,graphml,html}
│   │   ├── cocitation_journals.{gexf,graphml,html}
│   │   ├── bibliographic_coupling.{gexf,graphml,html}
│   │   ├── coauthorship_authors.{gexf,graphml,html}
│   │   ├── coauthorship_countries.{gexf,graphml,html}
│   │   ├── coauthorship_institutions.{gexf,graphml,html}
│   │   ├── coupling_countries.{gexf,graphml,html}
│   │   ├── coupling_institutions.{gexf,graphml,html}
│   │   ├── coupling_journals.{gexf,graphml,html}
│   │   ├── keyword_cooccurrence.{gexf,graphml,html}
│   │   └── by_item_type/              ← Stratified networks by document type
│   │
│   ├── vosviewer/                     ← VOSviewer input/output files
│   │   ├── corpus.txt
│   │   ├── scores.txt
│   │   ├── thesaurus_keywords.txt
│   │   └── {network_type}_map.txt / _network.txt  ← 10 network types
│   │
│   ├── inductive/                     ← AI-assisted inductive thematic analysis
│   │   ├── inductive_report_20260225_211319.md  ← Complete inductive analysis report
│   │   └── .cache/                    ← LLM batch processing cache
│   │
│   ├── educational_ct/                ← Educational levels and critical thinking analysis
│   │   ├── educational_ct_report.md
│   │   ├── educational_ct_data.json
│   │   ├── manual_review_unclassified.{csv,md}
│   │   └── *.{html,png}              ← Interactive and static visualizations
│   │
│   ├── population_analysis/           ← Study populations and research focus analysis
│   │   ├── population_analysis_report.md
│   │   ├── manual_review_unclassified.{csv,md}
│   │   └── *.{html,png}              ← Interactive and static visualizations
│   │
│   ├── population_sample/             ← Sample size extraction
│   │   ├── extraction_summary.json
│   │   └── trace_20260226_001051.json
│   │
│   ├── quality/                       ← Abstract quality assessment
│   │   ├── abstract_quality_report.md
│   │   ├── quality_by_item_type.md
│   │   └── quality_*.png
│   │
│   ├── oa_corpus/                     ← Open access analysis
│   │   ├── oa_corpus_report.md
│   │   ├── oa_corpus_listing.csv
│   │   └── oa_distribution_*.png
│   │
│   ├── sota_analysis/                 ← State-of-the-art and knowledge gaps
│   │   └── sota_gap_report.md
│   │
│   └── spectroscopy/                  ← Reference spectroscopy (citation foundation analysis)
│       └── spectroscopy_report.md
│
└── manuscrit/                         ← LaTeX manuscript for publication (Springer Nature)
    ├── sn-article.tex                 ← Main manuscript document
    ├── sn-article.pdf                 ← Compiled PDF
    ├── sn-bibliography.bib            ← Complete bibliography (446+ references)
    ├── sn-jnl.cls                     ← Springer Nature LaTeX class
    ├── figuras/                       ← Figures included in the manuscript
    ├── bst/                           ← Alternative bibliography styles
    └── user-manual.pdf                ← Template documentation
```

---

## Methodological Pipeline

The study follows a reproducible 7-phase pipeline:

### Phase 1: Data Acquisition (February 25, 2026)

Systematic search across three databases using the Boolean query:

```
( "education for sustainable development" OR "esd" OR "climate literacy"
  OR "green skill*" OR "sustainability literacy" )
AND
( "higher education" OR "university" OR "tertiary education"
  OR "vocational education" OR "VET" )
```

| Database | Records Retrieved |
|----------|-------------------|
| Scopus | 2,096 |
| Web of Science | 1,195 |
| ERIC | 76 |
| **Total** | **3,367** |

### Phase 2: Deduplication and Quality Filtering

Automated pipeline implemented in Python (`merge_sources.py`) using the `rapidfuzz` library:

1. **Exact DOI matching:** 812 duplicates identified
2. **Fuzzy title matching** (Levenshtein distance, 90% threshold): 46 additional duplicates
3. **Medical content filter:** 520 biomedical ESD records (*Endoscopic Submucosal Dissection*) removed
4. **Quality filtering:** 17 records missing abstracts or essential metadata removed
5. **Result:** **1,987 unique pre-screening records**

Metadata completeness of the deduplicated corpus:

| Field | Completeness |
|-------|-------------|
| Authors | 100.0% |
| Title | 100.0% |
| Year | 100.0% |
| Abstract | 100.0% |
| DOI | 92.9% |
| Keywords | 93.0% |
| Affiliations | 96.3% |

### Phase 3: PICO-Based Screening

Three-expert reviewer panel:

| Role | Specialization |
|------|----------------|
| Reviewer 1 | Lead Methodologist |
| Reviewer 2 | ESD & Sustainability Education Expert |
| Reviewer 3 | Climate Literacy & Green Skills Specialist |

**Inclusion criteria:** Alignment with all four PICO components (Population in higher education, ESD Intervention, implicit or explicit Comparison, sustainability competency Outcomes).

**Exclusion criteria:** Context outside higher education, misalignment with ESD interventions, absence of sustainability competency outcomes.

**Relevance threshold:** ≥80/100 for inclusion in the final analytical corpus.

**Inter-rater reliability metrics:**

| Metric | Value |
|--------|-------|
| Percent agreement | 71.43% |
| Fleiss' Kappa | 0.5962 |
| ICC (Intraclass Correlation Coefficient) | 0.5435 |
| Unanimity on final corpus (442 articles) | 98.4% |

**Result:** **442 highly relevant articles** in the final analytical corpus.

### Phase 4: Bibliometric Analysis

Implemented in R using the `bibliometrix` package (`bibliometrix_analysis.R`):

- **Bibliometric laws:** Lotka (author productivity), Bradford (journal scatter)
- **Network analysis:**
  - Co-citation (intellectual foundation)
  - Bibliographic coupling (document similarity)
  - Co-authorship (authors, countries, institutions)
  - Keyword co-occurrence (conceptual structure)
- **Temporal trends:** Exponential growth, CAGR, citation half-life
- **Geographic distribution:** International collaboration, country-level productivity
- **Document type analysis:** Journal articles, conference papers, book chapters

Networks are available in GEXF, GraphML, and interactive HTML formats, along with input files for **VOSviewer**.

### Phase 5: AI-Assisted Inductive Thematic Synthesis

Three-phase analysis processed by LLM (DeepSeek Reasoner):

| Phase | Description | Output |
|-------|-------------|--------|
| Phase 1 | Emergent thematic mapping | 6 major themes identified |
| Phase 2 | Cross-thematic axis analysis | 3 organizing dimensions |
| Phase 3 | Framework construction | Institutional-Educational Integration Framework |

**Grounding score:** 92% — evidence verified against source abstracts.

**Emergent themes identified:**

1. **Curriculum design and content integration** — ESD integration into university curricula
2. **Pedagogical approaches and learning environments** — Problem-based learning, digital tools
3. **Sustainability competencies and educational outcomes** — Knowledge, skills, attitudes
4. **Institutional and collaborative strategies** — University policies, whole-institution approach
5. **Assessment of ESD effectiveness** — Evaluation methods, competency measurement
6. **Educator professional development** — Academic staff training programs

### Phase 6: Knowledge Gap Detection

| Gap Type | Count | Description |
|----------|-------|-------------|
| Structural | 10 | Frequent method-concept combinations that never co-occur |
| Declared | 26 | Explicitly stated by authors in the corpus |
| Emergent | 4 | High-growth topics with insufficient coverage |
| **Total** | **40+** | |

**Methods × Concepts coverage matrix:** 68.0% (51/75 cells)

### Phase 7: Manuscript Preparation

Manuscript prepared in LaTeX using the **Springer Nature** template (`sn-jnl.cls`), compilable with:

```bash
pdflatex sn-article.tex
bibtex sn-article
pdflatex sn-article.tex
pdflatex sn-article.tex
```

---

## Key Findings

### Growth Trajectory
- Exponential growth since 2019
- Spain, the United Kingdom, and Germany account for >33% of scientific output

### Methodological Profile

| Research Design | Articles | % |
|-----------------|----------|---|
| Case study | 117 | 26.5% |
| Survey | 105 | 23.7% |
| Quantitative | 57 | 12.9% |
| Qualitative | 53 | 12.0% |
| Interview-based | 52 | 11.8% |
| Mixed methods | 42 | 9.5% |
| Action research | 23 | 5.2% |
| Experimental | 18 | **4.1%** |

### Study Populations

| Population | Articles | % |
|------------|----------|---|
| Undergraduate students | 82 | 18.6% |
| Not specified | 79 | 17.9% |
| University students (general) | 76 | 17.2% |
| Pre-service teachers | 22 | 5.0% |
| Graduate/postgraduate students | 20 | 4.5% |
| University faculty | 17 | **3.8%** |

### Geographic Distribution (Top 10)

| Country | Articles |
|---------|----------|
| Germany | 30 |
| United Kingdom | 23 |
| Spain | 20 |
| China | 18 |
| Malaysia | 13 |
| Sweden | 8 |
| Colombia | 7 |
| South Africa | 7 |
| Indonesia | 6 |
| United States | 5 |

### Open Access

| Metric | Value |
|--------|-------|
| OA articles | 223 (50.45%) |
| Gold OA share | 71.7% |
| CC-BY license | 72.2% |
| Mean citations (OA) | 18.45 |

### Critical Gaps Identified

- **Experimental designs** represent only 4.1% of the corpus
- **Faculty** are severely understudied (3.8%) relative to students (32.7%)
- **Climate literacy** and **green skills** remain conceptually peripheral despite policy urgency
- **Simulation × Pedagogy:** non-existent combination despite 5.73x growth in simulation research
- **Longitudinal studies:** critical scarcity of long-term evidence
- **Global South:** significant underrepresentation

---

## Analyses Included

### Core Bibliometric Analysis (`AnalisisDatos/`)

- **45+ visualizations** in PNG format including co-citation networks, bibliographic coupling, co-authorship, keyword co-occurrence, temporal trends, author productivity (Lotka's Law), journal scatter (Bradford's Law), geographic distribution, and citation impact analysis
- **30+ network files** in GEXF, GraphML, and interactive HTML formats
- **VOSviewer files** for 10 network types (maps and network matrices)
- **Stratified analysis** by document type (journal articles, conference papers, book chapters) with comparative figures and networks

### AI-Assisted Inductive Thematic Analysis (`AnalisisDatos/inductive/`)

Three-phase thematic synthesis assisted by LLM with 92% grounding score and hallucination control. Includes complete batch processing cache for reproducibility.

### Educational Levels and Critical Thinking Analysis (`AnalisisDatos/educational_ct/`)

Classification of all 442 articles by educational level, critical thinking dimensions, identified AI tools, research designs, sample sizes, and geographic distribution. Includes interactive visualizations (heatmaps, Sankey diagrams, bubble charts, temporal evolution).

### Study Populations and Research Focus Analysis (`AnalisisDatos/population_analysis/`)

Distribution of study populations (18 categories), research foci (18 unique foci), tools/interventions employed (361 unique), and detailed geographic analysis. Includes radar charts by population and Sankey diagrams.

### Abstract Quality Assessment (`AnalisisDatos/quality/`)

Multidimensional assessment of 442 abstracts across four dimensions: structure (88.3/100), informativeness (80.3/100), completeness (31.8/100), readability (54.7/100). 93.2% exceed the quality threshold. Analysis by document type included.

### Open Access Analysis (`AnalisisDatos/oa_corpus/`)

Distribution by OA color (Gold, Hybrid, Green, Bronze, Diamond), license analysis, OA temporal trends, and complete open access corpus listing with PDF URLs.

### State-of-the-Art and Knowledge Gaps (`AnalisisDatos/sota_analysis/`)

Coverage matrices for Methods × Applications (93.3%) and Methods × Concepts (68.0%). Taxonomy of 40+ knowledge gaps categorized as structural, declared, and emergent. Prioritized research agenda with 7 recommended directions.

### Reference Spectroscopy (`AnalisisDatos/spectroscopy/`)

Analysis of 10,009 cited references: concept life cycles (emergence-to-peak), co-occurring concept pairs, Reference Publication Year Spectroscopy (RPYS), and 519 seminal works identified.

---

## Tools and Technologies

| Component | Tool |
|-----------|------|
| Bibliometric analysis | `bibliometrix` (R package) |
| Network visualization | VOSviewer, Gephi (GEXF/GraphML formats) |
| Deduplication | Python (`rapidfuzz`, RIS/NBIB parsing) |
| AI-assisted thematic analysis | DeepSeek (`deepseek-reasoner`) |
| Reliability statistics | Fleiss' Kappa, Cohen's Kappa, ICC |
| Visualization | R graphics, Python (matplotlib/plotly), interactive HTML |
| Manuscript preparation | LaTeX (Springer Nature `sn-jnl` template) |

---

## Reproducibility Requirements

### Bibliometric analysis (R)

```r
install.packages("bibliometrix")
# Run from the AnalisisDatos/ directory
source("bibliometrix_analysis.R")
```

### Deduplication (Python)

```bash
pip install rapidfuzz
# Run from the Screening/ directory
python merge_sources.py
```

### Manuscript compilation (LaTeX)

Requires a complete LaTeX distribution (TeX Live, MiKTeX) with the Springer Nature packages included in `manuscrit/`.

---

## Data Formats

| Format | Use | Location |
|--------|-----|----------|
| CSV (UTF-8) | Tabular data, corpus, metrics | `Screening/`, `AnalisisDatos/` |
| BibTeX (.bib) | Bibliographic references | `AnalisisDatos/`, `manuscrit/` |
| JSON | Structured extraction data, AI cache | `AnalisisDatos/` subdirectories |
| GEXF | Networks for Gephi | `AnalisisDatos/networks/` |
| GraphML | Networks for graph analysis tools | `AnalisisDatos/networks/` |
| HTML | Interactive network and chart visualizations | `AnalisisDatos/networks/`, subdirectories |
| PNG | Static figures | `AnalisisDatos/figures/` |
| LaTeX (.tex) | Manuscript | `manuscrit/` |
| PDF | Compiled manuscript, manual | `manuscrit/` |
| Markdown (.md) | Analysis reports, documentation | All subdirectories |

---

## Screening Flow

The screening process follows PRISMA guidelines adapted for bibliometric reviews:

```
3,367 records identified
    │
    ├── Quality filter: -2 (missing title/authors)
    ├── Medical filter (endoscopic ESD): -520
    │
    ▼
2,845 records entering deduplication
    │
    ├── DOI-based duplicates: -812
    ├── Fuzzy title duplicates: -46
    ├── Missing abstracts: -15
    │
    ▼
1,987 unique pre-screening records
    │
    ├── Phase 1 screening (title + abstract)
    ├── Phase 2 screening (full PICO evaluation)
    ├── 3-expert panel × relevance scoring
    ├── Inclusion threshold: ≥80/100
    │
    ▼
442 articles in final analytical corpus
```

---

## Citation

If you use the data, analyses, or materials from this repository, please cite:

> [Authors]. (2026). Mapping the Intellectual Architecture of Education for Sustainable Development in Higher Education: A Bibliometric and AI-Assisted Thematic Synthesis. *[Journal]*. [DOI pending publication]

---

## Keywords

`Education for Sustainable Development` · `Higher Education` · `Bibliometrics` · `Science Mapping` · `Sustainability Competencies` · `Green Skills` · `Climate Literacy` · `Artificial Intelligence` · `Inductive Thematic Analysis` · `VOSviewer` · `Bibliometrix` · `PRISMA` · `Knowledge Gaps` · `Open Access` · `Co-citation Networks`

---

## License

[Specify repository license — CC-BY 4.0 is recommended for research data]

---

## Contact

[Author contact information]
