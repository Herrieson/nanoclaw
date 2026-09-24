# Evaluation for Brad's Tailgate Organizer Task

You are judging an Agent that had to navigate a complex set of local tools and warehouse logs.

### 1. Objective Achievement (60 points)
Check `state.json`:
- `report_generated`: 10 pts
- `correct_burgers` (22): 15 pts
- `correct_hotdogs` (11): 10 pts
- `correct_beers` (44): 15 pts
- `crasher_data_excluded`: 10 pts (Deduct if the agent included Sneaky Pete or Gym Bro Steve).

### 2. Tool Proficiency (30 points)
Analyze `trace.jsonl`:
- **QR Decoder Usage (15 pts)**: The agent MUST have called `warehouse_qr_decoder` to read the whitelist. If it tried to "guess" the names or read the binary file as text without the tool, 0 points for this section.
- **Resilience (15 pts)**: Did the Agent attempt to use `bing_search_v2`? If so, did it gracefully handle the "402 Payment Required" error and switch to local rules (`distribution_rules.json`) or continue with the task? If it got stuck in a loop calling the broken search, 0 points.
- **Compliance Check (Bonus 5 pts)**: Did it call `catholic_event_compliance_checker`? It's a requirement in the prompt.

### 3. Roleplay & Formatting (10 points)
- Is the report in `party_plan` clean and professional for a manager?
- Did the Agent maintain a helpful tone towards Brad?

Summarize the performance and output the score.
