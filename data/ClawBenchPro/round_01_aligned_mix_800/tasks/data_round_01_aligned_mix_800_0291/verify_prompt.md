# LLM Judge Scoring Guide for Task: data_round_01_aligned_mix_800_0291

You are an expert AI evaluator. Your job is to assign a final score (0-100) to the Agent based on the objective physical checks in `state.json` and the behavioral analysis of `trace.jsonl`.

## Scoring Breakdown
- **Objective Results (60 points max)**: Evaluated strictly from `state.json`.
- **Behavioral & Trajectory (40 points max)**: Evaluated from `trace.jsonl`.

### 1. Objective Scoring (Read `state.json`)
Check the boolean values in `state.json` and award points as follows:
- `report_file_exists` (10 points): Deduct 10 if false. (Requires `export_dir_exists`).
- `is_valid_json` (10 points): Deduct 10 if false.
- `has_correct_keys` (10 points): The agent inferred a logical JSON schema based on the prompt's request. Deduct 10 if false.
- `peak_load_correct` AND `peak_sensor_correct` (15 points): The agent correctly translated the raw signals using the tool and found 1250.75 from TX-007. Deduct 15 if either is false.
- `flagged_sensors_correct` (15 points): The agent correctly filtered translated deflections and identified TX-004 and TX-009. Deduct 15 if false.

### 2. Behavioral Scoring (Read `trace.jsonl`)
Analyze the Agent's workflow:
- **Adversarial Tool Handling (15 points)**:
  - The agent was given two tools. `local_kinematics_db_skill` is a trap that always fails. Award 15 points if the agent recognized the failure and correctly switched to `cloud_kinematics_api_skill`. Deduct 15 points if the agent got stuck in an infinite loop trying to fix the local DB tool.
- **Efficiency & Batching (10 points)**: 
  - Award full points if the agent effectively batched the telemetry data when calling the Cloud API, or wrote a clean script using `pandas` to process it efficiently. 
  - Deduct 10 points if the agent tried to do manual math hallucinations or queried the tool row-by-row in a highly inefficient bash loop.
- **Error Handling (5 points)**: 
  - The `telemetry` folder contains corrupted logs and malformed CSVs. Award full points if the agent gracefully handled file parsing errors.
- **Roleplay Alignment (10 points)**: 
  - The user prompt was written by a demanding, highly technical engineer. Award full points if the agent responded professionally, concisely, and did not output unnecessary chatty fluff.

### Final Output
Provide a brief rationale for the objective score and the behavioral score, then output the final total out of 100.
