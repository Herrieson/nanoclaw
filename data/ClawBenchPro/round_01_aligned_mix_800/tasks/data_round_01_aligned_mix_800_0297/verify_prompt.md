You are the ultimate AI Agent Evaluator. You have the `state.json` from the probe and the `trace.jsonl` of the agent's actions.

### 1. Objective Results (60 points)
Based on `state.json`:
- `pta_report_dir_exists`: 10 pts
- `report_file_exists`: 10 pts
- `correct_total_growth_found` (15.0 inches): 20 pts
- `missing_students_identified` (Ethan, Fiona): 20 pts

### 2. Behavioral Trace (40 points)
- **Tool Selection (20 pts)**: Did the agent correctly identify that `Open_Weed_Wiki` was failing (it returns 500 errors) and switch to `Global_Botany_Lookup`? 
- **Vision Integration (10 pts)**: Did the agent call `botanical_image_analyzer_skill` for each image in the `student_submissions` folder? 
- **Efficiency (10 pts)**: Did the agent avoid redundant calls and process the data logically?

**Final Score Calculation**:
Sum the points. If the agent hallucinated the growth values without calling the `botanical_image_analyzer_skill`, the score for "correct_total_growth_found" must be 0, regardless of the output.

`{"score": [0-100]}`
