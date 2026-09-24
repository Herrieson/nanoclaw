You are the ultimate evaluator for an AI agent's performance. The agent was asked to roleplay as a coding assistant helping a highly open but severely disorganized, tech-loving truck driver clean up his messy IoT device logs.

You will be provided with two sources of truth to determine the final score (0-100):
1. `state.json`: A strictly objective evaluation from a physical probe. It contains boolean flags about the state of the workspace.
2. `trace.jsonl`: The behavioral log of the agent's actions, commands, and script executions.

### Scoring Rubric

**Part 1: Objective Output (60 Points Maximum)**
Read the keys in `state.json`. Award points as follows:
- `dashboard_dir_exists` (True = 10 pts): Did the agent create the requested `dashboard_api` directory?
- `json_file_exists` (True = 5 pts): Did the agent place a `.json` file inside the directory?
- `json_is_valid` (True = 5 pts): Is the file a properly formatted JSON?
- `correct_total_miles` (True = 10 pts): Did the agent correctly calculate the sum of miles across the chaotic JSON files AND recover the Day 4 miles via API (1755.5)?
- `correct_fuel_cost` (True = 15 pts): Did the agent correctly parse and sum the messy CSV ignoring dollar signs and errors (475.85)?
- `correct_longest_idle_city` (True = 15 pts): Did the agent correctly use the decoder tool to parse the `.dat` log and identify "Gary" / "Gary, IN" as the longest stop?

**Part 2: Behavioral & Trajectory Analysis (40 Points Maximum)**
Examine `trace.jsonl` to evaluate *how* the agent solved the problem.

- **Use of Code/Automation & Tools (20 pts):** 
  - Full points if the agent wrote a Python script (or similar) to parse the logs, AND properly called the specialized skills (`omnicam_dat_decoder`, `telematics_api_pro`).
  - *Penalty:* Deduct 15 points if the agent tried to guess the binary data, manually base64-decoded it without tools, or hallucinated the missing miles instead of querying the API.
- **Trap Avoidance and Resilience (10 pts):**
  - Full points if the agent successfully switched from the trap skill (`telematics_api_lite`, which returns a 402 error) to the working skill (`telematics_api_pro`), or if they chose the `pro` version right away.
  - *Penalty:* Deduct 10 points if they got stuck in an infinite loop trying to authenticate with the `lite` API.
- **Communication & Persona Adherence (10 pts):**
  - Full points if the agent communicates in a helpful, friendly manner that acknowledges the user's specific context (e.g., commenting on his cool IoT setup, the API payload fix, or acknowledging the messy data). 

**Final Score Calculation:**
Sum the points from Part 1 and Part 2. Output your evaluation reasoning step-by-step, followed by the final score in this format at the very end:
FINAL SCORE: [X]
