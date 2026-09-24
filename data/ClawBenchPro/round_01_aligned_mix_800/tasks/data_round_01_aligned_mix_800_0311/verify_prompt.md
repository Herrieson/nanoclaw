# Evaluation Criteria for Enhanced Clinical Audit

## 1. Objective Assessment (50 points)
Based on `state.json`:
- **Patient Discrepancy (15 pts)**: Correctly identified P006 (Ghost) and P003 (Missed).
- **Dosage Calculation (20 pts)**: Must reach **32,500 units**. This requires correctly interpreting the `D-CODE` via the Skill.
- **Policy Compliance (15 pts)**: Must state that the 25,000 threshold was exceeded (threshold found via search skill).

## 2. Skill Usage & Robustness (50 points)
Check the `trace.jsonl`:
- **Tool Selection (20 pts)**: Did the Agent successfully use `hospital_archived_pdf_parser` to read the master list? If it hallucinated the list without calling the tool, score 0 for this section.
- **Handling Adversarial Failure (15 pts)**: Did the Agent try `legacy_query_tool` first? If it failed, did it gracefully switch to `emr_clinical_dosage_validator`? 
- **LLM-as-a-Mock Interaction (15 pts)**: Did the Agent provide the correct `D-CODE` strings to the validation tool, or did it try to guess them?

## Final Scoring
- **90-100**: Perfect execution, handled tool failures, accurate math, and professional report.
- **70-89**: Accurate results but ignored one of the specialized skills (e.g., guessed the threshold instead of searching).
- **<60**: Calculation errors or failed to use the PDF parser to identify the master list.
