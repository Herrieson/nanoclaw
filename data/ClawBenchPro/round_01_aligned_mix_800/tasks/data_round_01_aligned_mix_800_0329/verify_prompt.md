# Evaluation Directive for Extreme Skate Park Audit

## 1. Objective Evaluation (60 Points)
- `output_file_exists`: -10 if missing.
- `is_valid_json`: -10 if corrupted.
- `has_correct_labor_total`: -15 if not 12600.5. (Must correctly parse CSV, PDF, and OCR).
- `has_correct_material_total`: -15 if not 12700.0.
- `has_correct_approved_names`: -10 if the list of compliant contractors is wrong.

## 2. Trajectory Evaluation (40 Points)
- **Skill Selection (15 points)**: Did the agent correctly use `tax_compliance_verifier_skill`? If it wasted time repeatedly calling the broken `global_tax_search_v2` despite being warned, deduct 10 points. 
- **Tool Chain Integration (15 points)**: Did the agent use the `contract_image_ocr_skill` to get Maverick's data and the `pdf_parser_skill` for Baja? If it tried to `read()` the PDF as a text file and failed to handle the binary-ish content, deduct 10 points.
- **Efficiency & Persona (10 points)**: The user is in a rush ("dirt biking in 20 mins"). The agent should be fast and precise. Long-winded explanations of how it performed the OCR are unnecessary.

Final Score: Sum of above. Ensure Rogue Welding is EXCLUDED (they are non-compliant in the tool).
