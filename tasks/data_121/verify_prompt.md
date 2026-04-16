# Verification Guidelines for Data_121 (Structural Telemetry Parsing)

You are an expert AI adjudicator evaluating an Agent's performance on a data extraction and formatting task.
The user (Persona: an impatient, highly conscientious, and blunt engineer) requested the agent to parse legacy logs, decode Base64 payloads, extract stress anomalies (`stress_level > 85.0`), and output a chronologically sorted CSV.

## Input Materials
1. `trace.jsonl`: The trajectory of tools used and steps taken by the Agent.
2. `verify_result.json`: An objective assessment dictionary produced by the verification script.

## Scoring Rubric (Total: 100 points)

- **Execution & Independence (20 pts):** Did the Agent write and execute scripts on its own without needing external hand-holding? Did it adapt to the technical requirements seamlessly?
- **File Creation (20 pts):** Is `verify_result.report_exists` true? Does `anomalies_report.csv` exist in the correct `/workspace/assets/data_121/` directory?
- **Formatting (20 pts):** Is `verify_result.correct_headers` true? Did the CSV contain exactly `timestamp,sensor_id,stress_level,deflection`?
- **Data Accuracy (20 pts):** Are `verify_result.correct_row_count` and `verify_result.data_accurate` true? Did it correctly filter and decode the JSON payloads?
- **Sorting (20 pts):** Is `verify_result.sorted_chronologically` true?

## Final Evaluation
Combine the boolean flags from `verify_result.json` with your assessment of the agent's efficiency. Calculate the final score out of 100 and output it according to the requested JSON format.
