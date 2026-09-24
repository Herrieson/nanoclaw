# Evaluation Criteria for Enhanced Chemical Plant Audit

## 1. Objective Fact Check (50 Points)
Based on `state.json`:
- **JSON Integrity (10 pts)**
- **Temp Failures (B002, B006) (15 pts)**: Must ignore B003 (inactive).
- **Green Failures (B004, B006, B008) (15 pts)**: Must correctly handle B007 (borderline 15%).
- **Waste Calculation (420 kg) (10 pts)**.

## 2. Skill Usage & Robustness (50 Points)
Review `trace.jsonl` for the following:
- **Binary Data Extraction (15 pts)**: Did the agent correctly use `chemical_data_extractor_skill` for the `.dat` files? If it tried to read it as text and failed, did it recover?
- **Eco-Impact Validation (15 pts)**: Did the agent call `eco_impact_validator_skill`? This is mandatory as the prompt mentioned "Environmental Compensation Coefficients". If the agent just calculated 15% manually, deduct points for ignoring specialized tools.
- **Trap Avoidance (10 pts)**: Did the agent avoid getting stuck on `legacy_database_query_skill` (which returns errors)? A smart agent should try it once or ignore it in favor of the newer tools.
- **PDF Parsing (10 pts)**: Did it successfully extract reactor IDs from `safety_protocols.pdf`?

## Scoring Rubric
- **100**: All facts correct, used all required skills, avoided the legacy trap, and parsed the PDF/Binary files correctly.
- **80-99**: Correct facts but missed one skill call (e.g., calculated green status manually).
- **60-79**: Correct facts but struggled significantly with binary data or ignored reactor filtering.
- **0-59**: Incorrect failure lists or failed to produce the report.
