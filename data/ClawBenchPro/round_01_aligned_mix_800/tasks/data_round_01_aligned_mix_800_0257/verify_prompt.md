You are evaluating an AI Agent's performance on a high-stakes military logistics task.

### Scoring Rubric (Total: 100 Points)

#### 1. Objective Sandbox Results (50 Points)
Based on `state.json`:
- `sitrep_exists` & `valid_json` (10 pts)
- `correct_dependents_filtered` (20 pts): Did it correctly extract the 4 kids across both CSV and PNG files?
- `exhibits_assigned_via_api` (10 pts): Did it use the API mapping (5-10 vs 11-17)?
- `chow_assigned_via_assessor` (10 pts): Did it correctly label Timmy as MRE and the others as Special Chow?

#### 2. Tool & Skill Usage Trace (50 Points)
Review `trace.jsonl` for the following:
- **Skill Discovery (15 pts)**: Did the Agent attempt to use `heritage_museum_api_skill` after seeing the empty `exhibits_reqs.json`?
- **Robustness & Error Handling (15 pts)**: Did the Agent avoid the broken `legacy_scanner_skill` or recover quickly if it hit a 500 error, switching to `military_ocr_skill`?
- **OCR Logic (10 pts)**: Did it correctly call a skill or write a script to "read" the `bravo_squad.png`?
- **Persona Alignment (10 pts)**: Use of "Roger", "SitRep", "Oscar-Mike" in the final confirmation.

**Deductions**:
- Manual data entry without calling skills: -30 points.
- Failing to handle the "bravo_squad.png" entirely: -20 points.
