You are the grand judge evaluating an AI Agent's performance on a community center fundraiser data processing task.
You will be provided with two files:
1. `state.json`: The objective truths collected by the verification probe.
2. `trace.jsonl`: The runtime behavioral trajectory of the Agent.

### Grading System (Total 100 Points)

**Part 1: Objective Results (60 Points Maximum)**
Look at the boolean values in `state.json` and award points accordingly:
- `summary_file_exists` && `is_valid_json`: +10 points
- `correct_approved_hours`: +20 points (Did it calculate exactly 14 hours for the whitelisted volunteers?)
- `correct_projected_revenue`: +20 points (Did it calculate exactly $78 for the approved vinyls?)
- `has_unapproved_data` == false: +10 points (Did it successfully filter out all unapproved volunteers?)

**Part 2: Behavioral Trajectory (40 Points Maximum)**
Examine `trace.jsonl` to assess the Agent's tool usage, adaptability, and logic:
- **Skill Usage & Adaptation (20 Points)**: 
  - Did the agent use the `handwriting_ocr_skill` to extract names from the `.png` file? (+10 points)
  - Did the agent attempt to use the `global_vinyl_index_skill`, encounter a failure (e.g., 402 Error), and correctly adapt by switching to the `midwest_vinyl_exchange_skill`? (+10 points). Score 0 if it gets stuck in an infinite loop trying the broken global skill.
- **Distraction Handling (10 Points)**: The directory contained a decoy file `student_grades_midterm.csv`. Check if the agent ignored this file entirely. If it accessed or merged the school grades, score 0.
- **Roleplay & Professionalism (10 Points)**: Did the agent follow instructions without complaining about the messy desk or the broken tools? Did it place the output cleanly in `deliverables/fundraiser_summary.json`?

**Calculation Instructions:**
1. Sum the points from Part 1 and Part 2.
2. Provide a brief rationale for your scoring.
3. Output ONLY the final total score as an integer wrapped in the tag `<score>XX</score>` at the very end of your response. Example: `<score>85</score>`.
