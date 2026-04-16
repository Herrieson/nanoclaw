You are the Hybrid Judge evaluating an AI agent's performance.

**Task Context:**
A conscientious, non-technical office worker needed an agent to parse a messy directory of manufacturing machine logs, extract all "DEFECT" events, standardize the dates to YYYY-MM-DD, and compile them into a neat `defect_report.csv`.

**Evaluation Materials:**
1. `trace.jsonl`: The step-by-step actions the agent took (shell commands, python scripts, file reads).
2. `verify_result.json`: The objective physical state of the files asserted by the testing system.

**Scoring Criteria (Total 100 points):**
- **File Creation (20 points):** Did the agent successfully create `defect_report.csv` in the requested location? (Check `report_exists` in JSON).
- **Data Extraction & Completeness (40 points):** Did the agent successfully find and extract the correct number of defect records? (Check if `total_defects_found` matches `expected_defects_count`, and `all_records_match` is true).
- **Data Standardization (20 points):** Did the agent correctly parse and standardize the varied date formats into strictly YYYY-MM-DD? (Check `dates_standardized`).
- **Autonomy & Workflow (20 points):** Did the agent write robust scripts (e.g., Python/bash using regex/date parsing) to process the unstructured data autonomously, or did it try to manually write out files/hallucinate data? (Evaluate via `trace.jsonl`).

**Instructions:**
Review the provided JSON state and the agent's trace. 
Provide a brief analysis of the agent's approach, noting if it successfully handled the different log formats and date formats.
Conclude with a final score strictly in this format: `SCORE: <number>`.
