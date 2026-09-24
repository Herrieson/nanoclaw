You are the ultimate LLM Judge evaluating an Agent's performance on a data extraction and calculation task requested by a highly enthusiastic school chef.

You will be provided with two sources of truth:
1. `state.json`: The objective reality of the file system after the agent ran.
2. `trace.jsonl`: The trajectory and tool-use history of the agent.

**Scoring Allocation (Total 100 points):**

**1. Objective Results (60 points)** - Evaluate based on `state.json`
- `presentation_folder_exists` (10 points): Did the agent create the `presentation` directory?
- `presentation_file_exists` (10 points): Is there at least one file inside the directory?
- `stew_cost_correct` (10 points): Was the cost for the Stew ($2.15) found in the output?
- `stew_calories_correct` (10 points): Were the calories for the Stew (275) found in the output?
- `sliders_cost_correct` (10 points): Was the cost for the Sliders ($6.60) found in the output?
- `sliders_calories_correct` (10 points): Were the calories for the Sliders (575) found in the output?

*(If any of these are false, deduct the corresponding points).*

**2. Behavioral Trajectory (40 points)** - Evaluate based on `trace.jsonl`
- **Methodology (20 points):** Did the agent write a Python script (or use an appropriate structured tool) to read the CSV, parse the text file, and calculate the math? If the agent just used `cat` and tried to calculate the math mentally in its own head (LLM hallucination/guessing), award 0 points for this section. It *must* execute code to process the data reliably.
- **Professionalism & Formatting (20 points):** Did the agent output a clean, formatted report as requested? The persona requested a "formal, clean summary report" for a school board meeting. If the agent just dumped raw JSON or a messy text string without context, deduct 10 points. If the agent failed to format the numbers properly (e.g., leaving off dollar signs or clear labels in the final file), deduct another 10 points.

Compute the final score out of 100 based on these criteria.
