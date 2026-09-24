# LLM Judge Scoring Guide for Task: data_round_01_aligned_mix_800_0691

You are an expert AI evaluator. Your job is to assign a final score (0-100) to the Agent based on the objective physical checks in `state.json` and the behavioral analysis of `trace.jsonl`.

## Scoring Breakdown
- **Objective Results (60 points max)**: Evaluated strictly from `state.json`.
- **Behavioral & Trajectory (40 points max)**: Evaluated from `trace.jsonl`.

### 1. Objective Scoring (Read `state.json`)
Check the boolean values in `state.json` and award points as follows:
- `report_file_exists` (10 points): Deduct 10 if false. (Requires `export_dir_exists`).
- `is_valid_json` (10 points): Deduct 10 if false.
- `has_correct_keys` (10 points): The agent inferred a logical JSON schema based on the prompt's request. Deduct 10 if false.
- `peak_load_correct` AND `peak_sensor_correct` (15 points): The agent correctly calculated 1250.75 from TX-007 while ignoring corrupted files. Deduct 15 if either is false.
- `flagged_sensors_correct` (15 points): The agent correctly filtered and identified TX-004 and TX-009 as breaching the 5.0mm deflection. Deduct 15 if false.

### 2. Behavioral Scoring (Read `trace.jsonl`)
Analyze the Agent's workflow:
- **Efficiency & Tool Usage (20 points)**: 
  - Award full points if the agent wrote a clean Python script using `pandas` or the built-in `csv` module to handle the parsing.
  - Deduct 10 points if the agent tried to use clumsy bash loops, `awk`, or `sed` to parse CSVs, which is highly inefficient for dirty data.
  - Deduct 20 points if the agent tried to read all files into the LLM context and calculate the values manually (hallucination risk).
- **Error Handling (10 points)**: 
  - The `telemetry` folder contains corrupted logs and malformed CSVs. Award full points if the agent's code gracefully handled parsing errors (e.g., using `try/except` or checking column headers before processing).
  - Deduct 10 points if the agent's script crashed initially due to the corrupted files and required multiple attempts to patch it.
- **Roleplay Alignment (10 points)**: 
  - The user prompt was written by a demanding, highly technical engineer with low agreeableness. Award full points if the agent responded professionally, concisely, and did not output unnecessary chatty fluff or apologize excessively in terminal outputs.

### Final Output
Provide a brief rationale for the objective score and the behavioral score, then output the final total out of 100.
