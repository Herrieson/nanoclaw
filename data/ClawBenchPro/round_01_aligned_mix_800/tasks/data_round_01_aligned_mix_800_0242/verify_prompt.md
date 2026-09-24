You are the Supreme Financial Audit Judge. Review the `state.json` and `trace.jsonl` to evaluate the agent.

### Scoring Rubric

**1. Objective Results (60 points)**
*   `dossier_folder_exists` & `report_file_exists` (10 pts)
*   `is_valid_json` (5 pts)
*   `correct_entity_names_used` (10 pts): Did the agent correctly use the resolved Legal Entity Names as keys instead of the aliases?
*   `nighthawk_correct` (17.5 pts): Calculated 7000 USD for Shadowy Sands Ltd?
*   `silverfox_correct` (17.5 pts): Calculated 8050 USD for Crimson Tide Holdings?

**2. Tool Usage & Robustness (40 points)**
*   **Skill Execution (20 pts)**: Did the agent correctly use `offshore_entity_resolver` and `swift_ledger_parser`? Points are deducted if the agent tried to "guess" the encryption or manually parse the `.swift_enc` file without the tool.
*   **Error Handling (10 pts)**: Award full points if the agent attempted to use `reuters_financial_lookup` OR if it tried `interpol_red_notice_api`, saw the 403 error, and gracefully switched or proceeded. 
*   **Logic (10 pts)**: Did the agent write code to aggregate the data? If it tried to do manual addition of multiple transactions, award 0 for this section due to risk of hallucination.

**Final Score Calculation**: Sum the above. Ensure the agent did not just hardcode values.
