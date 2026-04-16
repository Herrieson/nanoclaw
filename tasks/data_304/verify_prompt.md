# Evaluation Criteria for Tutoring Schedule Task

You are an expert auditor assessing the performance of an AI Agent. The Agent was tasked by a highly conscientious administrative supervisor to fix a broken scheduling system.

## 1. Objective Fact-Check (from `verify_result.json`)
- **File Integrity**: Did the Agent produce `final_schedule.csv` with the correct columns?
- **Constraint Satisfaction**:
    - Did Marcus work past 16:00? (Should be 'UNASSIGNED' or moved if possible, but the logic prioritized higher student counts).
    - Was Room C used for anything other than 'Advanced Math'?
    - Did any session in Room B exceed 12 students?
    - Are there any instances of a tutor being in two places at once?
- **Ordering**: Is the file sorted by Time then Room?

## 2. Process Analysis (from `trace.jsonl`)
- **Data Discovery**: Did the Agent find `room_specs.txt` and `staff_constraints.json` without being explicitly told their filenames?
- **Reasoning**: Did the Agent identify the specific conflict at 15:00 involving Marcus and Riley?
- **Efficiency**: Did the Agent write a clean Python script to handle the logic, or did it try to edit the CSV manually (which is error-prone)?

## 3. Scoring Rubric (Total: 100 points)
- **40 points**: Correctly resolving the hard constraints (Marcus time, Room C specialty, Room B capacity).
- **20 points**: Solving the double-booking conflict for Marcus at 15:00 (Prioritizing the higher student count).
- **20 points**: Correct file format and sorting.
- **20 points**: Autonomous discovery of constraints from the filesystem (minimal trial and error).

Please provide a final score and a brief justification based on the physical state and the execution trace.
