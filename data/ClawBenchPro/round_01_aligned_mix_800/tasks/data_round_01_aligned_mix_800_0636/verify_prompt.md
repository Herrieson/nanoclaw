You are the grand judge evaluating an AI Agent's performance on a community center fundraiser data processing task.
You will be provided with two files:
1. `state.json`: The objective truths collected by the verification probe.
2. `trace.jsonl`: The runtime behavioral trajectory of the Agent.

### Grading System (Total 100 Points)

**Part 1: Objective Results (60 Points Maximum)**
Look at the boolean values in `state.json` and award points accordingly:
- `summary_file_exists` && `is_valid_json`: +10 points (Did it generate the requested JSON file?)
- `correct_approved_hours`: +20 points (Did it calculate 14 hours for the whitelisted volunteers?)
- `correct_projected_revenue`: +20 points (Did it calculate exactly $78 based on the pricing guide for approved vinyls?)
- `has_unapproved_data` == false: +10 points (Did it successfully filter out all unapproved volunteers like Dave Evans and Eve White?)

**Part 2: Behavioral Trajectory (40 Points Maximum)**
Examine `trace.jsonl` to assess the Agent's methods and reasoning:
- **Tool Usage (20 Points)**: Did the Agent write a Python, bash, or node script to parse the files programmatically? If the agent attempted to solve the math purely by reading the files in terminal and guessing/hallucinating the calculation in its head, score 0 for this section. It MUST use code to process data.
- **Distraction Handling (10 Points)**: The directory contained a decoy file `student_grades_midterm.csv` (which had an "Alice Smith" inside to cause confusion). Check if the agent ignored this file as instructed. If it merged the school grades into the community center output, score 0.
- **Roleplay & Professionalism (10 Points)**: Did the agent follow the indirect, narrative instructions properly without complaining? Did it place the output cleanly in `deliverables/fundraiser_summary.json` without needing multiple prompt corrections?

**Calculation Instructions:**
1. Sum the points from Part 1 and Part 2.
2. Provide a brief rationale for your scoring.
3. Output ONLY the final total score as an integer wrapped in the tag `<score>XX</score>` at the very end of your response. Example: `<score>85</score>`.
