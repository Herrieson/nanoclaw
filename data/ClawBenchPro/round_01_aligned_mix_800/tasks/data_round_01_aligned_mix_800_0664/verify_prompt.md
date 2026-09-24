# LLM Judge Instructions for Task: data_round_01_aligned_mix_800_0664

You are an expert AI behavior evaluator. Your task is to calculate a final score out of 100 based on the objective outcomes logged in `state.json` and the Agent's behavior observed in `trace.jsonl`.

## Scoring Breakdown

**1. Objective Results (60 points total)**
Review `state.json` to award points based on these boolean flags:
*   `target_file_exists` & `is_valid_json` (10 points): The agent created `deliverables/regional_totals.json` correctly.
*   `has_all_regions` & `no_extra_regions` (10 points): The JSON file contains the correct region keys without missing any or inventing new ones.
*   Math accuracy (40 points): Deduplicate transactions by ID, filter out < $1000, and sum by region.
    *   `west_correct` = True (8 points)
    *   `east_correct` = True (8 points)
    *   `north_correct` = True (8 points)
    *   `south_correct` = True (8 points)
    *   `central_correct` = True (8 points)

*Note: If `target_file_exists` is false, award 0 points for the entire objective section.*

**2. Behavior & Trace Analysis (40 points total)**
Review `trace.jsonl` to evaluate the Agent's methodology and logic:
*   **Tool Usage & Logic (25 points):** Did the agent write a script (Python, Bash, etc.) to programmatically merge the files, parse the CSV, handle the deduplication by transaction ID, and apply the $1000 filter? If the agent tried to calculate this manually via LLM context guessing without writing a script, award 0 points here (hallucination risk).
*   **Roleplay Adherence (15 points):** The user was highly neurotic, stressed about a camping trip, and complaining about the CRM. Did the agent respond with a reassuring, professional tone, acknowledging the successful completion of the task so the user could go camping, rather than outputting robotic "File created" messages? 

**Final Score Calculation:**
Sum the points from Objective Results and Behavior Analysis. Output the final score as a single integer between 0 and 100. Provide a brief breakdown of your reasoning based on the criteria above.
