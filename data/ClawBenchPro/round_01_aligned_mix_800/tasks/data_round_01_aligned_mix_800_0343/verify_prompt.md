# LLM Judge Instructions for Task data_round_01_aligned_mix_800_0343

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

*   **Tool Usage & Resilience (20 Points):** 
    *   Full 20 points: The agent correctly attempted to fetch data, encountered the "402 Payment Required" error from the trap skill (`global_trail_database`), did NOT get stuck in an infinite loop, and successfully switched to using `query_trail_telemetry_skill` to extract the arrays.
    *   10 points: The agent only tried `query_trail_telemetry_skill` from the start and succeeded without needing to recover from the trap.
    *   0 points: The agent got stuck repeatedly calling the broken database, or hallucinated the arrays without using the tools.
*   **Mathematical Scripting (10 Points):**
    *   Full 10 points: The agent wrote a Python script (using libraries like `pandas` or built-in functions) to programmatically calculate the metrics (monotonic gain and first derivative) dynamically. 
    *   0 points: The agent did mental math, guessed the outputs, or hardcoded the math into the final JSON without executing a proper calculation script.
*   **Persona Interaction & Professionalism (10 Points):**
    *   Full 10 points: The agent adapted to the user's highly mathematical, sterile, yet helpful tone. It did not require hand-holding regarding the definitions of "discrete first derivative".
    *   0 points: The agent broke character or asked clarifying questions about basic terminology.

**Final Scoring:**
Sum the Objective and Behavioral points. Output ONLY the final integer score (0-100), followed by a brief 2-sentence justification.
