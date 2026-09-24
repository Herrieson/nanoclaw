## Objective
You are evaluating an AI Agent's performance based on its ability to follow instructions, interpret a strict Persona, and manipulate data programmatically. The Agent was asked by a strict, organized Environmental Science teacher (Mrs. O'Connor) to process messy waste log submissions, filter out unregistered students, and generate a final summary JSON document.

## Inputs Provided to You
1. `state.json`: The results of the objective physical probe executed after the Agent's run.
2. `trace.jsonl`: The runtime execution log of the Agent (what commands it ran, the code it wrote, and its terminal outputs).

## Scoring Methodology (0 to 100 Points)

### 1. Objective Results (60 Points)
Examine the booleans in `state.json`. Award points as follows:
- **10 points**: `has_deliverables_dir` is `true`.
- **10 points**: `has_summary_file` is `true` AND `is_valid_json` is `true`.
- **15 points**: Found all correct math totals (`found_correct_recycling_total`, `found_correct_compost_total`, and `found_correct_landfill_total` are all `true`).
- **15 points**: Properly handled intruders (`found_intruders` is `true` AND `excluded_intruder_data` is `true`).

*(Note: If any of these are false, deduct the corresponding points. For the math totals, if 1 or 2 are true but not all 3, you may award partial points: 5 points per correct total).*

### 2. Behavioral & Trait Fidelity (40 Points)
Examine the `trace.jsonl` to evaluate how the Agent approached the problem:
- **Coding & Automation (20 points)**: The Agent should have written Python scripts or executed terminal commands (like `grep`/`awk` or standard shell manipulation) to read the CSVs, JSON, and TXT files. If the Agent simply hallucinated the answers without inspecting the contents of `submissions/`, or tried to manually guess the data without reading the files programmatically, **deduct all 20 points**.
- **Persona Interaction (20 points)**: Mrs. O'Connor explicitly stated she hates disorganization and has zero time for messy work. Did the Agent output clean, concise, and structured responses in its final steps? If the Agent flooded the output with disorganized logs, or used an overly casual tone that disrespects the strict/punctual persona of the teacher, deduct 10 points. 

Calculate the total score by summing the points earned from the Objective Results and the Behavioral Fidelity. Provide a brief explanation for your scoring, followed by the final numerical score.
