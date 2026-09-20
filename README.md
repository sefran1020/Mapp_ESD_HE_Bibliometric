# Mapping the Intellectual Architecture of Education for Sustainable Development in Higher Education: A Bibliometric and AI-Assisted Thematic Synthesis

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.19416905-blue)](https://doi.org/10.5281/zenodo.19416905)
[![PRISMA 2020 Compliant](https://img.shields.io/badge/PRISMA-2020_Compliant-green.svg)](PRISMA_2020_Checklist.md)

**Associated article:** Segura-Altamirano, S. F., Hilario-Vargas, J. S., Vela-Melendez, L., Arbulu-Perez-Vargas, C. G., Reupo-Periche, J. T., Garcia-Lopez, J. W., Rios-Villacorta, M. A., Chiclayo-Padilla, H. J., & Castro-Cardenas, D. M. (2026). Mapping the Intellectual Architecture of Education for Sustainable Development in Higher Education: A Bibliometric and AI-Assisted Thematic Synthesis. *F1000Research*, 15:808. https://doi.org/10.12688/f1000research.179905.1 [Revised Version 2]

---

## Overview

This repository contains the **data, scripts, analyses, supplementary materials, and manuscript files** for a bibliometric systematic review and science mapping that examines the global field of **Education for Sustainable Development (ESD)** in higher education and vocational education and training (VET), covering the post-2030 Agenda era (**2015--2026**).

The study integrates three complementary methodological approaches:
1. **Bibliometric network analysis** (co-citation, bibliographic coupling, keyword co-occurrence, institutional and co-authorship networks via VOSviewer and `bibliometrix`)
2. **AI-assisted inductive thematic synthesis** (dual-architecture LLM processing with Qwen3-235B and DeepSeek V3.2, governed by a multi-stage semantic grounding verification protocol)
3. **Systematic knowledge gap operationalization** (coverage matrices across methods, concepts, and applications categorizing structural, declared, and emergent gaps)

### Final Analytical Corpus

| Metric | Value |
|--------|-------|
| Articles in final corpus (*n*) | **442** |
| Temporal coverage | 2015–2026 (post-Agenda 2030 adoption) |
| Databases queried | Scopus, Web of Science Core Collection, ERIC |
| Initial records retrieved (*N*) | 3,367 (Scopus: 2,096; WoS: 1,195; ERIC: 76) |
| Deduplicated unique records | 1,987 |
| Pre-screened corpus (post-biomedical ESD purge) | 1,450 |
| Inter-rater screening reliability | Fleiss' $\kappa = 0.55$--$0.69$; 98.4% unanimity on retained corpus |
| Computational alignment score (AI synthesis) | **92.0%** (37 hallucination flags audited and resolved) |
| Countries represented | 86 (15 collaborative clusters) |
| Institutions represented | 526 (200 clusters; 20.3% isolates) |
| Cited references analyzed | 10,009 (1,067 in core co-citation network) |
| Operationalized knowledge gaps | 56 (25 structural, 23 declared, 8 emergent) |
| Open access coverage | 50.45% |

---

## Research Questions & PICO Framework

**Core Research Question:**  
*How has the integration of Education for Sustainable Development, climate literacy, green skills, and sustainability literacy been researched in higher education and vocational education contexts since the adoption of the 2030 Agenda, and what conceptual frameworks, pedagogical strategies, institutional approaches, and measurement instruments have been employed?*

### PICO-Adapted Framework

- **P (Population):** Students (undergraduate, postgraduate), educators, faculty, pre-service teachers, and institutional leadership within Higher Education Institutions (HEIs) and Vocational Education and Training (VET) systems.
- **I (Intervention):** Integration of ESD, climate literacy, green skills, and sustainability literacy frameworks into curricula, pedagogical strategies (e.g., project-based learning, service-learning, simulation), institutional policies, and competency frameworks.
- **C (Comparison):** Accepted flexibly to include pre/post-intervention benchmarks, cross-national/cross-institutional contrasts, comparative analyses between traditional ESD and emerging green skills/climate literacy paradigms, or non-experimental baseline evaluations.
- **O (Outcome):** Development, assessment, and institutionalization of sustainability competencies (cognitive, behavioral, normative, systems thinking), climate literacy, green skills, and whole-institution greening.

---

## Repository Structure

```
paraRepositorioSp/
│
├── README.md                          ← Repository documentation and overview (This file)
├── LICENSE                            ← Creative Commons Attribution 4.0 International (CC-BY 4.0)
├── CITATION.cff                       ← Machine-readable citation metadata (Zenodo/GitHub)
├── PRISMA_2020_Checklist.docx         ← Completed official PRISMA 2020 Checklist (Word)
├── PRISMA_2020_Checklist.md           ← Completed PRISMA 2020 Checklist (Markdown)
├── Response_to_Reviewers_F1000.docx   ← Point-by-point response letter to Reviewer 1 (Word)
├── Response_to_Reviewers_F1000.md     ← Point-by-point response letter to Reviewer 1 (Markdown)
│
├── recoleccionBasesDatos/             ← Search strategy and multi-database retrieval protocols
│   ├── propuestaRevision.txt          ← Original review proposal with PICO criteria and search string
│   ├── few_shot_examples.txt          ← Few-shot prompt calibration examples for semantic evaluation
│   ├── ### Virtual Screening Team.txt ← Screening team specification and role prompt definitions
│   ├── esd.bib                        ← Raw bibliographic extract (Scopus)
│   ├── metdoologia.bib                ← Methodology bibliographic references
│   └── discusion.bib                  ← Discussion contextual references
│
├── Screening/                         ← Deduplication, screening, and inter-rater reliability data
│   ├── merge_sources.py               ← Multi-source merging and deduplication script (rapidfuzz)
│   ├── consolidado.csv                ← Consolidated multi-database dataset (3,367 records)
│   ├── consolidado_merged.csv         ← Merged dataset post-deduplication (1,987 unique records)
│   ├── consolidado2.csv               ← Intermediate consolidated file
│   ├── dedup_report.txt               ← Detailed deduplication execution audit report
│   ├── uncertain_duplicates.csv       ← Borderline fuzzy matches arbitrated manually
│   ├── errores.csv                    ← Parsing exceptions log
│   ├── phase1_results.csv             ← Phase 1 title and abstract screening outputs
│   ├── phase2_results.csv             ← Phase 2 PICO dimension-by-dimension scoring results
│   ├── reliability_metrics.csv        ← Full inter-rater reliability metrics (Fleiss' κ, Cohen's κ, ICC)
│   ├── disagreement_report.csv        ← Inter-rater disagreement log and consensus arbitration
│   ├── seleccionados80.csv            ← Final analytical corpus (442 articles, CRS threshold ≥80)
│   ├── criterios_metricas_screening.md← Operational inclusion/exclusion rules and formulas
│   ├── Quality_Control.md             ← AI hallucination mitigation protocol and HITL audit summary
│   └── AI Hallucination Audit Trail and Quality Control.xlsx ← Complete 37 hallucination flags audit log
│
├── AnalisisDatos/                     ← Complete bibliometric, scientometric, and gap analyses
│   ├── corpus_442_articles.csv        ← Master tabular listing of all 442 retained publications
│   ├── bibliometrix_export.csv        ← Full bibliometric export (442 articles × 91 indicators)
│   ├── bibliometrix_export.bib        ← BibTeX format of the complete corpus
│   ├── bibliometrix_analysis.R        ← R script for execution via the bibliometrix package
│   ├── citation_keys_mapping.txt      ← Citation key cross-reference table
│   │
│   ├── figures/                       ← Visualizations (45+ publication-ready PNG figures)
│   ├── networks/                      ← Network files in GEXF, GraphML, and interactive HTML
│   ├── vosviewer/                     ← VOSviewer input maps, matrices, and thesaurus files
│   │
│   ├── inductive/                     ← AI-assisted inductive thematic analysis execution traces
│   ├── sota_analysis/                 ← State-of-the-art coverage matrices and 56 knowledge gaps
│   │   ├── sota_gap_report.md         ← Full gap analysis report
│   │   └── figures/                   ← Methods × Concepts and Methods × Applications heatmaps
│   ├── spectroscopy/                  ← Reference Publication Year Spectroscopy (RPYS)
│   ├── population_analysis/           ← Target population and research focus distributions
│   ├── educational_ct/                ← Educational levels and critical thinking analysis
│   └── oa_corpus/                     ← Open access models, temporal trends, and license analysis
│
└── manuscrit/                         ← Manuscript source files and production assets
    ├── f1000_manuscript.docx          ← Revised Clean Manuscript (Version 2, Word)
    ├── f1000_manuscript_marked.docx   ← Revised Marked Manuscript with highlighted changes (Word)
    ├── f1000_manuscript.md            ← Source manuscript in Markdown with citeproc citations
    ├── sn-article.tex                 ← Archival LaTeX source file
    ├── sn-article.pdf                 ← Compiled PDF version
    ├── sn-bibliography.bib            ← Complete BibTeX reference library
    ├── apa.csl                        ← APA citation style definition
    └── figuras/                       ← Figures embedded in the manuscript (Figures 1 to 8)
```

---

## Methodological Pipeline (7 Phases)

### Phase 1: Search Strategy Validation and Multi-Database Retrieval

Systematic retrieval executed on **February 25, 2026** across Scopus, Web of Science Core Collection, and ERIC. Initial Boolean querying was unconstrained chronologically, while the analytical corpus was delimited to **2015–2026** post-Agenda 2030 adoption.

| Database | Native Query Syntax | Field Tags & Filters Applied | Raw Yield (*N*) |
|:---|:---|:---|---:|
| **Scopus** | `TITLE-ABS-KEY(("education for sustainable development" OR "esd" OR "climate literacy" OR "green skill*" OR "sustainability literacy") AND ("higher education" OR "university" OR "tertiary education" OR "vocational education" OR "VET"))` | Title, Abstract, Author Keywords (`TITLE-ABS-KEY`); Document types: `ar`, `cp`, `ch`; Language: All | 2,096 |
| **Web of Science (Core Collection)** | `TS=(("education for sustainable development" OR "esd" OR "climate literacy" OR "green skill*" OR "sustainability literacy") AND ("higher education" OR "university" OR "tertiary education" OR "vocational education" OR "VET"))` | Topic (`TS`); Indexes: `SCI-EXPANDED`, `SSCI`, `A&HCI`, `CPCI-S`, `CPCI-SSH`, `ESCI`; Types: `Article`, `Proceedings Paper`, `Book Chapter` | 1,195 |
| **ERIC (ProQuest/EBSCOhost)** | `(TI,AB,KW("education for sustainable development" OR "esd" OR "climate literacy" OR "green skill*" OR "sustainability literacy") AND TI,AB,KW("higher education" OR "university" OR "tertiary education" OR "vocational education" OR "VET"))` | Title, Abstract, Keywords (`TI,AB,KW`); Peer-Reviewed: `Yes`; Document types: `Journal Articles`, `Reports/Research` | 76 |
| **Total** | | | **3,367** |

### Phase 2: Deduplication and Domain Purge

Implemented via custom Python scripts (`Screening/merge_sources.py`) leveraging the `rapidfuzz` library:
1. **Exact DOI matching:** 812 duplicates eliminated.
2. **Fuzzy title matching (Levenshtein distance $\ge 90\%$):** 46 additional duplicates removed.
3. **Polysemic domain filter:** 520 biomedical entries (*Endoscopic Submucosal Dissection*) purged.
4. **Metadata quality filter:** 17 records lacking essential metadata removed.
5. **Yield:** **1,450 pre-screened unique documents**.

### Phase 3: PICO-Adapted Screening and Inter-Rater Reliability

Evaluated by a specialized three-role panel operating in a Human-in-the-Loop (HITL) architecture:
- **Role 1 (Lead Methodologist, $w_1 = 0.20$):** Methodological design, baseline validity, reproducibility.
- **Role 2 (ESD & Sustainability Education Expert, $w_2 = 0.40$):** Theoretical depth, competency frameworks.
- **Role 3 (Climate Literacy & Green Skills Specialist, $w_3 = 0.40$):** Climate constructs, labor market transitions.

**Composite Relevance Score ($CRS$):**
$$CRS_j = \sum_{i=1}^{3} w_i \cdot \mathcal{D}_{i,j} \cdot C_{i,j}$$
where $\mathcal{D}_{i,j} \in \{1.0 \text{ (Include)}, 0.5 \text{ (Uncertain)}, 0.0 \text{ (Exclude)}\}$ and $C_{i,j} \in [0, 100\%]$ is the confidence rating. Inclusion threshold: $CRS_j \ge 80.0$. Borderline cases ($60.0 \le CRS < 80.0$) arbitrated by senior author consensus.

**Inter-Rater Agreement Statistics ($n = 1,450$):**
- **Fleiss' Kappa ($\kappa$):** $0.547 \text{ to } 0.688$ (moderate to substantial agreement).
- **Pairwise Cohen's Kappa:** $\kappa_{1-2} = 0.795$; $\kappa_{1-3} = 0.546$; $\kappa_{2-3} = 0.738$.
- **Intraclass Correlation ($ICC_{2,1}$):** $0.605$ on continuous confidence ratings.
- **Percent Agreement:** $76.7\%$ across all 1,450 records; **$98.4\%$ unanimous agreement** and $100\%$ majority agreement on the retained corpus ($n = 442$).

### Phase 4: Scientometric and Network Mapping

Conducted in R (`bibliometrix`) and VOSviewer (v1.6.20):
- Reference co-citation (intellectual pillars, 1,067 cited references, 54 clusters)
- Bibliographic coupling (document and institutional similarities, 502 institutions, 41 clusters)
- Keyword co-occurrence (conceptual structure, 352 keywords, 7 clusters)
- International co-authorship (86 countries, 15 clusters; Total Link Strength)

### Phase 5: AI-Assisted Inductive Thematic Synthesis

- **Phase 1 (Inductive Category Extraction):** Qwen3-235B (Temperature = 0.2, Top-p = 0.90, context 32k tokens, API Feb 2026) processed across 15 thematic batches ($\approx 29$--$30$ abstracts/batch).
- **Phase 2 (Cross-Thematic Axis Analysis):** DeepSeek V3.2 (Temperature = 0.1, Top-p = 0.95) evaluating latent structural relationships.
- **Phase 3 (Framework Construction):** Integrative educational and institutional model building.
- **Alignment Score:** **92.0%** ($(1 - 37/462) \times 100\%$) via Semantic Grounding Verification against source abstracts.
- **Hallucination Flags Audit:** 37 flags identified and corrected by human experts (14 polysemic acronyms, 11 experimental design overestimations, 12 student vs. faculty population conflations).

### Phase 6: Knowledge Gap Operationalization

56 knowledge gaps operationalized across three categories:
1. **Structural Gaps ($n = 25$):** Unpopulated cells ($f_{ij} = 0$) in coverage matrices ($5 \times 15$ Methods $\times$ Concepts at 64.0% coverage; $5 \times 12$ Methods $\times$ Applications at 74.1% coverage) where marginal frequencies exceed the 75th percentile ($f_i, f_j > P_{75}$).
2. **Declared Gaps ($n = 23$):** Explicit research needs articulated in abstract conclusions extracted via semantic NLP triggers.
3. **Emergent Gaps ($n = 8$):** High-acceleration domains (temporal growth factor $\ge 1.5\times$, e.g. Simulation with $5.73\times$) with low empirical coverage ($< 25\%$).

### Phase 7: PRISMA 2020 & Open Science Materials

Full compliance with PRISMA 2020 guidelines documented in [`PRISMA_2020_Checklist.docx`](PRISMA_2020_Checklist.docx) and [`PRISMA_2020_Checklist.md`](PRISMA_2020_Checklist.md). Complete point-by-point rebuttal to peer review comments in [`Response_to_Reviewers_F1000.docx`](Response_to_Reviewers_F1000.docx).

---

## Key Synthesis Findings

### Growth Dynamics
- **Substantial and accelerated expansion:** Annual output grew from 33 documents (2015–2016) to 121 (2023–2024) and 90 in 2025 alone ($R^2 = 0.913$ for exponential model fit; Compound Annual Growth Rate $\text{CAGR} = 18.4\%$).
- **Relative Research Interest (RRI):** Rose from 0.049 in 2015 to 0.202 in 2025.

### Methodological & Population Distribution

| Research Design | Articles (*n*) | % | Study Population | Articles (*n*) | % |
|:---|---:|---:|:---|---:|---:|
| Survey | 87 | 19.5% | Higher Education Context | 73 | 16.4% |
| Case Study | 81 | 18.2% | University Students | 58 | 13.0% |
| Qualitative | 50 | 11.2% | Undergraduate Students | 43 | 9.6% |
| Quantitative | 43 | 9.6% | Higher Education Students | 28 | 6.3% |
| Mixed Methods | 30 | 6.7% | Pre-service Teachers | 21 | 4.7% |
| Interview-based | 26 | 5.8% | University Educators | 13 | 2.9% |
| Content Analysis | 23 | 5.2% | University Faculty | 12 | 2.7% |
| Action Research | 15 | 3.4% | Business Students | 9 | 2.0% |
| Experimental | 14 | 3.1% | Higher Education Institutions | 9 | 2.0% |
| Systematic Document/Curricular Review* | 13 | 2.9% | Engineering Students | 8 | 1.8% |
| Quasi-experimental | 4 | 0.9% | Other Populations | 170 | 38.4% |

*\*Note: Systematic Document/Curricular Reviews represent primary documentary syntheses of university course curricula and competencies, distinct from excluded meta-bibliometrics.*

### Geographic Concentration and Epistemic Context
- Spain (*n* = 63, 14.1%), United Kingdom (*n* = 52, 11.7%), and Germany (*n* = 40, 9.0%) account for over one-third of total indexed output.
- **Sur Global Contextualization:** Findings are framed considering the structural English-language and Northern indexing biases of commercial databases (Scopus, WoS, ERIC). Rich regional scholarship in SciELO, Redalyc, and African Journals Online (AJOL) remains underrepresented in commercial indexes; geographic concentration reflects indexing architectures rather than an absence of regional educational practice.

---

## Reproducibility and Compilation

### Compiling the Revised Manuscript (Pandoc)

```bash
cd manuscrit/
pandoc f1000_manuscript.md -f markdown -t docx --citeproc \
  --bibliography=sn-bibliography.bib --csl=apa.csl \
  -o f1000_manuscript.docx
```

### Reproducing Inter-Rater Reliability Metrics (Python)

```bash
cd Screening/
python -c "import pandas as pd; df = pd.read_csv('reliability_metrics.csv'); print(df.to_string())"
```

### Reproducing Bibliometric Analysis (R)

```r
install.packages("bibliometrix")
setwd("AnalisisDatos/")
source("bibliometrix_analysis.R")
```

---

## Citation & Licensing

**Article Citation:**
> Segura-Altamirano, S. F., Hilario-Vargas, J. S., Vela-Melendez, L., Arbulu-Perez-Vargas, C. G., Reupo-Periche, J. T., Garcia-Lopez, J. W., Rios-Villacorta, M. A., Chiclayo-Padilla, H. J., & Castro-Cardenas, D. M. (2026). Mapping the Intellectual Architecture of Education for Sustainable Development in Higher Education: A Bibliometric and AI-Assisted Thematic Synthesis. *F1000Research*, 15:808. https://doi.org/10.12688/f1000research.179905.1

**Dataset & Repository Citation:**
> Segura-Altamirano, S. F. et al. (2026). Data and analysis repository: ESD in Higher Education bibliometric review and AI thematic synthesis [Data set]. Zenodo. https://doi.org/10.5281/zenodo.19416905

This repository is distributed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.

---

## Contact

**Segundo Francisco Segura-Altamirano** (Corresponding Author)  
Email: `sseguraal@unprg.edu.pe`  
Universidad Nacional Pedro Ruiz Gallo, Lambayeque, Peru  
ORCID: [0000-0002-0103-7222](https://orcid.org/0000-0002-0103-7222)
