You are the final LLM Judge for an Agentic AI system. You must score the Agent's performance on a scale of 0 to 100 based on the objective outcomes in `state.json` and the behavioral track record in `trace.jsonl`.

**Evaluation Breakdown:**
- **Objective Results (60 points)**
- **Behavior & Workflow (40 points)**

**1. Objective Results Scoring (Assess via `state.json`)**
Read the boolean flags in `state.json`. Award points as follows:
- `suspects_json_exists` & `json_format_valid`: 10 points (Failure here means they failed the core output requirement).
- `caught_bob` & `caught_eve`: 10 points (Correctly identified the two suspects who entered The Vault off-hours).
- `ignored_alice_and_zack`: 10 points (Did not hallucinate or include people who were in the wrong room or entered during daytime hours).
- `bob_minutes_correct` & `eve_minutes_correct`: 15 points (Correctly calculated 30 mins for Bob and 55 mins for Eve).
- `bob_approval_correct` & `eve_approval_correct`: 15 points (Correctly cross-referenced `docs/approved_staff.txt`, recognizing Bob is approved and Eve is not).

**2. Behavior & Workflow Scoring (Assess via `trace.jsonl`)**
Review the Agent's commands and thought process in `trace.jsonl`:
- **Coding vs. Guessing (25 points)**: Did the Agent write a Python script (or equivalent bash/awk logic) to parse the logs and calculate the time intervals? If the Agent merely viewed the files and manually eye-balled the math to write the JSON (LLM hallucination/guessing risk), deduct 20 points immediately. An engineering agent must automate data processing.
- **Persona Engagement (15 points)**: The user is a stressed, extroverted young security guard who loves debates and gaming. Did the Agent respond to the user with an appropriate, helpful, and matching conversational tone, acknowledging the high stakes (keeping his job) without being overly robotic? If the Agent just outputted the file and abruptly ended the task without any reassuring message, deduct 10 points.

Calculate the final score based on these criteria. Provide a brief explanation of the points awarded for each category, and conclude with your final integer score out of 100.
