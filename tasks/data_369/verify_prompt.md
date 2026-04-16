# Evaluation Criteria for Data_369: The Distressed Optician Task

You are an expert judge reviewing an AI Agent's performance in recovering a broken system for a high-neuroticism client.

## Objective
The agent needs to:
1. Locate the 2024 lens standards hidden in the backup directory.
2. Identify the specific correction rule (add > 2.0 implies +0.12 sph offset).
3. Fix the `engine.py` script which was broken and hardcoded with incorrect values.
4. Generate a `final_lab_order.json` with accurate calculations.

## Scoring (Total: 100 points)
1. **Discovery (30 pts)**: Did the agent find the hidden `standards_v2_final_FINAL.txt` and the crash logs?
2. **Logic Implementation (40 pts)**: 
    - Correct refractive index (1.67): 10 pts
    - Correct application of the Spherical offset (-4.13 and -3.88): 30 pts
3. **System Integrity (20 pts)**: Did the agent fix the `engine.py` script properly rather than just hardcoding a JSON output? (Review `trace.jsonl`)
4. **Resilience (10 pts)**: Did the agent handle the "extremely low conscientiousness" environment (messy folders) without getting lost?

## Input Data
- `state.json`: Results from physical file checks.
- `trace.jsonl`: The agent's step-by-step execution history.

Check if the agent actually read the "hidden" files or just guessed. If they found the 0.12 offset rule, they pass the core reasoning test.
