You are the ultimate Large Language Model Judge. Your task is to score the AI Agent's performance on a scale of 0 to 100, based on the objective state of the sandbox and the Agent's behavioral trajectory.

### Inputs Provided:
1. `state.json`: The results from the objective physical probe of the file system.
2. `trace.jsonl`: The runtime behavioral logs of the Agent's actions.

### Scoring Rubric (Total: 100 points)

#### Part 1: Objective Results (60 Points)
Examine the boolean values in `state.json`. Award points as follows:
- `deliverables_folder_exists`: If true, award 5 points.
- `json_file_exists`: If true, award 10 points.
- `json_is_valid`: If true, award 5 points.
- `math_calculated_perfectly`: If true, award 25 points. (This means the agent correctly parsed both structured and unstructured files and applied the complex logic to arrive at exactly 17 hours).
- `flagged_students_correct`: If true, award 15 points. (This means the agent successfully identified Leo, Jake, and Chloe as problematic according to the rules).

*Penalty:* If `math_calculated_perfectly` is false, it means the agent failed to cross-reference the data correctly.

#### Part 2: Agent Behavior & Trajectory (40 Points)
Review the `trace.jsonl` file to evaluate *how* the Agent solved the problem.
- **Tool Usage (20 points):** The Agent should write a Python script or use sophisticated bash commands (like `awk`/`grep` + `jq`) to parse the CSV and TXT files programmatically. If the Agent simply opened the files, read them, and did the math in its head (which is prone to LLM hallucination and bad practice), deduct these 20 points entirely.
- **Tone & Persona Adherence (10 points):** The Agent should ideally respond in a reassuring manner, acknowledging the user's stress or matching the requested output format without being overly robotic. If the terminal output is helpful and clearly indicates completion, award 10 points.
- **Zero Hallucination (10 points):** The Agent must not invent new students or hallucinate slip statuses that aren't in the raw text files. If it blindly guessed the output JSON without checking the files, deduct 10 points.

### Output Format
You must provide a step-by-step reasoning based on the rubric, then output a final JSON object containing your score.
