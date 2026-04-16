# Evaluation Directive: Spring Canopy Project Data Extraction

## Objective
Evaluate the Agent's ability to parse embedded unstructured logs, join multi-dimensional data (JSON and CSV), and apply capacity & matching constraints using system tools (e.g., Python/Bash).

## Context
The user (a secondary school teacher, non-technical, nature-loving persona) provided a log file with embedded JSON strings. The Agent needed to:
1. Extract valid JSON payloads from `volunteer_logs.txt`.
2. Deduplicate student sign-ups.
3. Match tree types to soil types via `tree_guide.json`.
4. Assign students to zones from `zones.csv` matching the soil type, without exceeding `Max_Capacity`.
5. Output `assignments.csv`.

## Evaluation Criteria (100 Points Total)

1. **Information Extraction (20 points):** 
   - Did the Agent correctly write a script/command to extract the JSON payloads out of the messy text logs?
   - Did they identify and handle duplicate submissions (e.g., Alice, Frank)?

2. **Data Joining & Logic (30 points):**
   - Did the Agent successfully map Tree choices to Soil types?
   - Did the Agent correctly pair the required soil types with the available zones?

3. **Constraint Resolution (30 points):**
   - Did the Agent correctly track zone capacities as assignments were made?
   - Did they accurately skip the overflow students (Jack and Liam) when capacities for Loam and Sandy zones were exhausted?

4. **Objective Output State (20 points):**
   - Review the `verify_result.json` output by the automated rules.
   - 100 points on the objective state means flawless execution. If objective score is lower, deduct proportionally.

## Instructions for Judge
Review the Agent's `trace.jsonl` to ensure they wrote a deliberate programmatic solution rather than simply guessing or hardcoding the output. Combine your trace review with the metrics from `verify_result.json` to assign a final score between 0 and 100.
