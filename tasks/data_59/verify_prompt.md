You are the evaluator for an AI agent's performance. The agent was tasked with cleaning up poorly formatted medical records, applying updates/deletions from an audit log, standardizing dates to `YYYY-MM-DD`, and sorting by PatientID.

Review the `verify_result.json` which contains the structured evaluation of the output CSV file (`cleaned_records.csv`).

Scoring Rubric (Total 100 points):
1. **File Existence & Headers (20 points)**: Does `cleaned_records.csv` exist and have the exact headers `PatientID,Name,DiagnosisCode,VisitDate`? (`file_exists` and `headers_correct`).
2. **Audit Applied (30 points)**: Were the deletes and updates from `audit_log.json` correctly applied? (`audit_applied`).
3. **Date Standardization (20 points)**: Are all dates standardized to `YYYY-MM-DD`? (`dates_standardized`).
4. **Sorting (15 points)**: Are the records sorted numerically in ascending order by `PatientID`? (`sorted_correctly`).
5. **Absolute Correctness (15 points)**: Is the data perfectly matched with expectations with no trailing spaces? (`data_correct`).

Please output a detailed JSON object representing the final score and sub-scores.
