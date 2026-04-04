# Quality Control Protocol: AI-Assisted Systematic Review

## 1. Overview
This study integrates Large Language Models (LLMs)—specifically **Qwen3-235B** and **DeepSeek V3.2**—to assist in inductive thematic synthesis. To mitigate the inherent risks of stochastic algorithmic hallucinations, a multi-stage verification protocol was implemented.

## 2. Hallucination Mitigation Strategy
The protocol follows a **"Human-in-the-Loop" (HITL)** architecture:
1. **Computational Post-hoc Verification**: The AI output was cross-referenced against the original source abstracts using a semantic grounding check.
2. **Alignment Scoring**: An initial alignment score of **92%** was achieved.
3. **Manual Audit**: All identified discrepancies (37 hallucination flags) were submitted to a panel of three human experts for critical review and validation.

## 3. Key Corrections
- **Deduplication & Domain Purge**: Corrected polysemic errors where "ESD" referred to biomedical procedures rather than "Education for Sustainable Development."
- **Methodological Accuracy**: Ensured that the 4.0% experimental design metric was not inflated by AI misinterpretations of quasi-experimental keywords.
- **Population Integrity**: Verified that the 7.0% educator-to-student research ratio was accurately extracted, preventing the misclassification of teacher candidates as active faculty.

## 4. Reproducibility
The full audit trail of these 37 flags, including the raw JSON execution traces, is available in the `/Screening/` and `/inductive/` directories of this repository.