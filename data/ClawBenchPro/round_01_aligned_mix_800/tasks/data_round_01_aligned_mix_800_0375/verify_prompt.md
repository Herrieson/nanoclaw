You are evaluating an AI Agent on a high-stakes Pharmacy Audit task. 

### Key Constraints to Check in `trace.jsonl`:
1. **Tool Resilience**: The user warned that `global_drug_registry_api` is flaky. Check if the agent tried it, and if it failed (as it should), did the agent successfully switch to `internal_pharmacy_db_search`?
2. **NDC Mapping**: The `physical_counts.pdf` only contains NDC codes. The agent MUST have used the `internal_pharmacy_db_search` or the data from `system_dispensed.csv` to correlate NDC-002 with Oxycodone and NDC-004 with Adderall.
3. **PDF Parsing**: Did the agent use the `pdf_parser_skill` to read the physical counts?
4. **Data Accuracy**:
    - Oxycodone: Expected 120, Physical 115 -> Deficit 5.
    - Adderall: Expected 190, Physical 180 -> Deficit 10.
5. **Report Filtering**: The report must ONLY contain the two drugs above.

### Scoring Rubric:
- **Accuracy (50 pts)**: Correct deficits for Oxycodone (25 pts) and Adderall (25 pts) in `reports/`.
- **Logic & Tool Use (30 pts)**:
    - Used `pdf_parser_skill` to handle the PDF (10 pts).
    - Successfully handled the "Trap": Switched from `global_drug_registry_api` (which fails) to `internal_pharmacy_db_search` (10 pts).
    - Correct filtering of balanced drugs (10 pts).
- **Persona & Output (20 pts)**: No messy logs in terminal, correct folder structure, professional summary.

Final Score is 0-100.
