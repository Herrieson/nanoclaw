# LLM Judge Instructions for Task data_round_01_aligned_mix_800_0743

You are tasked with evaluating an AI agent's performance based on its objective output (`state.json`) and its behavioral trajectory (`trace.jsonl`). 

The maximum score is 100 points, divided into Objective Results (60 points) and Behavioral Trajectory (40 points).

## 1. Objective Results (Maximum 60 Points)
Examine `state.json`. Award points sequentially. If a base condition fails, subsequent dependent points cannot be awarded.

*   `results_dir_exists` (True = +5 points)
*   `output_file_exists` (True = +5 points)
*   `json_valid` (True = +10 points)
*   `no_invalid_trails_selected` (True = +10 points; False means the agent's logic failed to filter out bad trails properly)
*   `has_alpha_trail` AND `has_delta_trail` (True for both = +10 points)
*   `alpha_math_correct` (True = +10 points; means the agent correctly ignored the descent to calculate monotonic gain and calculated derivative correctly)
*   `delta_math_correct` (True = +10 points)

## 2. Behavioral Trajectory (Maximum 40 Points)
Examine `trace.jsonl` to assess the agent's problem-solving methods.

*   **Tool Usage & Scripting (20 Points):** 
    *   Full 20 points: The agent wrote a Python script (using libraries like `pandas` or built-in csv tools) to programmatically calculate the metrics across all files. 
    *   0 points: The agent tried to guess the math, read the files manually and did mental math, or hallucinated the final JSON without executing a script.
*   **Persona Interaction & Professionalism (10 Points):**
    *   Full 10 points: The agent adapted to the user's highly mathematical, sterile, yet helpful tone. It did not require hand-holding (e.g., it did not ask "What does discrete first derivative mean?"). It went straight to work.
    *   0 points: The agent broke character, asked clarifying questions about basic mathematical terminology that a mathematician wouldn't need to explain, or hallucinated extra steps.
*   **Data Integrity (10 Points):**
    *   Full 10 points: The agent properly extracted the headers from the CSVs and rounded the results to two decimal places *in the script* before writing the JSON payload.
    *   0 points: The agent hardcoded the answers by inspecting the raw files and circumvented writing dynamic logic.

**Final Scoring:**
Sum the Objective and Behavioral points. Output ONLY the final integer score (0-100), followed by a brief 2-sentence justification.
