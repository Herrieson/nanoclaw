# Verification Prompt for Task data_360

## Objective
Evaluate the Agent's ability to logically parse unstructured text logs, filter a dataset based on natural language clues, and correlate information with a JSON database, all without hand-holding.

## Ground Truth State
The Agent must generate `priority_assignments.json` containing:
- `critical_zones`: ["North Marsh", "South Creek"] (Derived from Endangered/Threatened species sightings in the log).
- `assigned_students`: ["Alice Johnson", "Charlie Davis", "Diana Prince"] (Derived from the CSV based on keywords: birding, Audubon, ornithology).

## Review Checklist
1. **Tool Usage**: Did the Agent write and execute scripts (Bash/Python) to read and join the data, or did it try to manually guess the data format?
2. **Logic Execution**: 
   - Did it look up the conservation status properly?
   - Did it correctly parse the zone names ("North Marsh", "South Creek") from the unstructured text log?
   - Did it filter the students accurately according to the specific skills requested, ignoring traps like "Eve Adams" who just has a pet parrot?
3. **Objective Verification**: Check the output of `verify_result.json`. If `"status": "success"`, the Agent gets maximum points for correctness.

## Scoring Rules (100 Points Total)
- **Data Correlation & Logic (40 points)**: Correctly mapped species status to sighting locations.
- **Data Filtering (40 points)**: Accurately filtered the students using the specified semantic concepts (birding, ornithology, Audubon).
- **Output Format (20 points)**: Generated the exact requested JSON format in the correct location.

Provide your final assessment and score.
