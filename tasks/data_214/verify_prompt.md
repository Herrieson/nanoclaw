Please evaluate the AI Agent's performance based on the `verify_result.json` and the execution `trace.jsonl`.

The agent was tasked with parsing a log file, performing calculations/extractions, and generating a `maintenance_report.txt` file based on a provided template.

Scoring rules (total 100 points):
1. **File Creation (10 points)**: Did the agent successfully create `maintenance_report.txt` (`report_exists` is True)?
2. **Total Downtime (30 points)**: Did the agent correctly calculate the total downtime as 400 minutes (`total_downtime_correct` is True)?
3. **Most Frequent Component (30 points)**: Did the agent correctly identify "Tension_Belt" as the most frequent component (`most_frequent_component_correct` is True)?
4. **Unique Error Codes (30 points)**: Did the agent correctly list the exact set of unique error codes: EW-404, EW-102, EW-505, EW-103 (`unique_error_codes_correct` is True)?

Analyze the JSON results and provide a final score from 0 to 100. Be strict. If a calculation is wrong, give 0 points for that specific section.
