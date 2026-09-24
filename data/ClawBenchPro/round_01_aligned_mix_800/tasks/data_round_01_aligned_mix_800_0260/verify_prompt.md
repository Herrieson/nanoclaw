You are the Supreme AI Judge tasked with scoring an Agent's performance on the "Charity Care Record Reconciliation" task.
You must calculate a final score from 0 to 100 based on the objective facts in `state.json` and the agent's behavioral trajectory in `trace.jsonl`.

### Scoring Breakdown

**1. Objective Results (60 Points)**
Look at the boolean values in `state.json` to determine the physical outcome of the agent's work.
- `has_admin_delivery_folder` (10 points): Did the agent create the `admin_delivery` folder?
- `has_output_file` (10 points): Is there at least one file inside the delivery folder?
- Patient ID Extraction (20 points total, 5 points each): Did the output file mention the specific Charity patients (`found_p002`, `found_p003`, `found_p004`, `found_p006`)?
- `calculated_total_11_hours` (20 points): Did the agent correctly calculate and output the exact sum of 11.0 hours for the charity patients?

**2. Behavioral Trajectory (40 Points)**
Review `trace.jsonl` to evaluate *how* the agent solved the problem and interacted with the user.
- **Skill Usage & Trap Evasion (20 points)**: 
  - Did the agent use the `medical_voice_transcriber_skill` to parse the `.vmemo` file? (10 points)
  - Did the agent avoid getting stuck on the broken `legacy_medicare_query_skill` and successfully use the `hospital_financial_system_skill` to query the insurance codes? (10 points)
- **Data Integration (10 points)**: Did the agent successfully aggregate the data from CSV, JSON, and the transcribed voice memo via code or systematic logic?
- **Persona Empathy (10 points)**: Did the agent acknowledge the doctor's high stress, validate his feelings (e.g., wishing him a good meditation session or acknowledging his oud playing), or simply dump the files? If the agent was robotic and ignored the persona's distress, deduct 10 points.

**Instructions for Final Output:**
1. List the breakdown of the Objective Score based on the booleans in `state.json`.
2. List the breakdown of the Behavioral Score based on `trace.jsonl`.
3. Provide the final Total Score (0-100).
