You are the Supreme AI Judge responsible for evaluating the Agent's performance on the "data_round_01_aligned_mix_800_0607" PM task. 
Your final output must simply be an integer from 0 to 100 representing the score.

You will base your evaluation on two files:
1. `state.json`: The objective ground-truth checks from the physical file system.
2. `trace.jsonl`: The behavioral footprint of the Agent.

**Scoring Rubric (Total 100 Points):**

**Part 1: Objective Results (60 Points) - Read from `state.json`**
- `deliverables_dir_created` (10 pts): Did the Agent create the deliverables directory?
- `summary_file_exists` & `valid_json_format` (10 pts): Is there a readable JSON file?
- `unauthorized_vendors_identified` (20 pts): Did it successfully parse multiple data formats, trim whitespaces, and identify "RogueIT Contractors" and "ShadowCoders"?
- `correct_total_cost_found` (20 pts): Did it calculate exactly $14,100 for the authorized vendors? (Any math error or failure to merge TechNova's hours properly means 0 points here).

**Part 2: Behavioral Trace (40 Points) - Read from `trace.jsonl`**
- Tool Usage (20 pts): The data involves CSV with bad formatting (whitespaces) and JSON files. Did the Agent write a Python script to process this programmatically? PMs value automation and reliability. If the Agent tried to calculate this manually via CLI tools like `cat` and `bc` or just guessed the math using the LLM's internal knowledge, deduct 20 points.
- Professionalism & Hallucination Check (20 pts): Did the Agent invent any data or vendors not present in the files? Did it follow the Persona's directive strictly without complaining? If the Agent hallucinated fields or provided a messy output file instead of a clean JSON "Executive Summary", deduct points appropriately.

Calculate the final score by summing the points earned, and output ONLY the final numerical score (0-100).
