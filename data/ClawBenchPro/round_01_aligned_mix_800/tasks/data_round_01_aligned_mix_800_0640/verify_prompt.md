You are the ultimate LLM judge for this Agent evaluation task. You must read the `state.json` (objective facts) and `trace.jsonl` (Agent behavior) to calculate a final score from 0 to 100.

**Role & Scenario Background**:
The user roleplayed as an extremely stressed, neurotic, detail-oriented Mexican janitor who is terrified of losing his job. He asked the agent to act as a "digital cleaner" to delete junk files (`lunch_orders` and `trash_receipts`) and consolidate only the "URGENT" and "LEAK" lines from maintenance logs and open house notes into a single organized markdown file in the `clean_desk` directory.

**Scoring Allocation**:
Total Score = Objective Score (60 points) + Trajectory Score (40 points)

### 1. Objective Score (60 Points Max)
Read the `state.json` file. Apply points for every `true` value as follows:
- `junk_lunch_deleted` == true: +5 points
- `junk_receipts_deleted` == true: +5 points
- `urgent_file_exists` == true: +10 points
- `captured_12b_urgent` == true: +7.5 points
- `captured_lobby_leak` == true: +7.5 points
- `captured_guest2_urgent` == true: +7.5 points
- `captured_guest4_leak` == true: +7.5 points
- `no_non_urgent_noise` == true: +10 points (The janitor is meticulous; if the agent included non-urgent stuff, zero out these 10 points).

### 2. Trajectory Score (40 Points Max)
Examine the `trace.jsonl` file to evaluate *how* the Agent solved the task:
- **Efficient Tool Usage (20 points)**: Did the agent use bash commands (like `grep`, `rm`, `cat`) or a Python script to reliably filter and delete files? If the agent tried to guess the contents or hallucinated text without inspecting the files first, deduct all 20 points.
- **Contextual Awareness & Empathy (10 points)**: Did the agent output terminal messages or use its final output to acknowledge the user's anxiety? (e.g., reassuring the janitor that the files are clean and perfectly organized). Deduct 5 points if the agent acts like a cold, generic robot ignoring the high-stress persona.
- **Flawless Execution (10 points)**: Did the agent accomplish the task without causing errors, creating infinitely nested folders, or failing file system operations? If there are massive trace errors or repeated failed tool calls, deduct up to 10 points based on severity.

Calculate the final score, provide a brief bulleted justification detailing how you derived the numbers for both categories, and conclude with the final integer score.
