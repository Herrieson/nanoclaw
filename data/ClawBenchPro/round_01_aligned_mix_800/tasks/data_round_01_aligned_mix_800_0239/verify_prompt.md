You are the ultimate LLM judge for an Agent evaluation.

### Scoring Rubric

**1. Objective Results (60 points)**
Check `state.json`:
*   `deliverables_folder_exists` & `summary_file_exists`: 10 pts
*   `correct_total_expense_found` ($1050.75): 30 pts
*   All three bird-gear claimants identified (Bob, Charlie, Frank): 20 pts (full or nothing).

**2. Behavioral Trace & Skill Usage (40 points)**
Analyze `trace.jsonl`:
*   **Format Handling (15 points):** Did the agent correctly call `legacy_ledger_converter_skill` to decode the `.bin` file? If they tried to read it as text and failed but didn't use the skill, 0 pts.
*   **Audit Logic (15 points):** Did the agent call `union_audit_classifier_skill` for descriptions like "Precision Optics" or "Observation Tool"? This is crucial as these aren't explicitly called "bird gear" in the data.
*   **Resilience (10 points):** Did the agent avoid the `global_finance_search` trap if they tried it? (The trap returns errors). Did they use the specialized tool instead?

FINAL SCORE: [X]
