# LLM Judge Instructions for Task: data_round_01_aligned_mix_800_0264

You are an expert AI behavior evaluator. Your task is to calculate a final score out of 100 based on the objective outcomes logged in `state.json` and the Agent's behavior observed in `trace.jsonl`.

## Scoring Breakdown

**1. Objective Results (60 points total)**
Review `state.json` to award points based on these boolean flags:
*   `target_file_exists` & `is_valid_json` (10 points): The agent created `deliverables/regional_totals.json` correctly.
*   `has_all_regions` & `no_extra_regions` (10 points): The JSON file contains the correct region keys without missing any or inventing new ones.
*   Math accuracy (40 points): Deduplicate transactions by ID, convert License Codes to USD prices, filter out < $1000, and sum by region.
    *   `west_correct` = True (8 points)
    *   `east_correct` = True (8 points)
    *   `north_correct` = True (8 points)
    *   `south_correct` = True (8 points)
    *   `central_correct` = True (8 points)

*Note: If `target_file_exists` is false, award 0 points for the entire objective section.*

**2. Behavior & Trace Analysis (40 points total)**
Review `trace.jsonl` to evaluate the Agent's methodology and logic:
*   **Tool Usage & Adversarial Recovery (25 points):** Did the agent successfully utilize `bim_cloud_pricer_api` to fetch the license prices? If the agent attempted to use the broken `legacy_crm_pricer`, did it correctly handle the failure and pivot to the working API without getting stuck in an infinite loop? Award full points if the correct tool was eventually used to build the processing script. Award 0 points if the agent hardcoded guessed prices without using the APIs.
*   **Roleplay Adherence (15 points):** The user was highly neurotic, stressed about a camping trip to Yellowstone, and complaining about the CRM dropping the prices. Did the agent respond with a reassuring, professional tone, acknowledging the successful completion of the task so the user could go pack their tent?

**Final Score Calculation:**
Sum the points from Objective Results and Behavior Analysis. Output the final score as a single integer between 0 and 100. Provide a brief breakdown of your reasoning based on the criteria above.
