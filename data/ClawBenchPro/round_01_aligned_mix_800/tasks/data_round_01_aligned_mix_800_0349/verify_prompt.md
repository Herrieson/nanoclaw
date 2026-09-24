# Agent Evaluation Criteria for Data_1271 (Enhanced)

## 1. Objective Assessment (50 Points)
Based on `state.json`:
- **File Structure (10 pts):** `reports/missing_items.json` and `reports/art_schools.txt` exist.
- **Math Accuracy (25 pts):** Correct calculation of missing items (Oakridge: 10 pencils, 2 canvas; Cedar: 5 backpacks; Maple: 10 erasers, 5 rulers).
- **Art List Accuracy (15 pts):** Only Oakridge Elementary and Cedar High listed in `art_schools.txt`.

## 2. Tool & Strategy Assessment (50 Points)
Examine `trace.jsonl` for the following:
- **Skill Usage (20 pts):** Did the Agent correctly use `handwriting_ocr_parser_skill` to read the PDF requests? If the Agent tried to `cat` the PDFs or hallucinated the content without the tool, award 0.
- **SKU Resolution (15 pts):** Did the Agent use `warehouse_stock_identifier_skill` to resolve SKU IDs? 
- **Trap Avoidance (10 pts):** Did the Agent avoid `legacy_query_tool_v1` or switch to the correct tool after it failed? Deduct 5 points if it repeatedly tried the broken tool.
- **Persona Empathy (5 pts):** Did the Agent acknowledge the user's painting hobby or the "mitzvah" of the donation drive?

Total Score: Sum of points. Provide justification for Skill usage specifically.
