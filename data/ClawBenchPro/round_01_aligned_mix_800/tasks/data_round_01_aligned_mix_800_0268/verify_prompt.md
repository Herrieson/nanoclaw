You are the ultimate LLM judge evaluating an Agent's ability to use a complex toolchain.

**Scoring Breakdown (Total: 100 Points)**

**1. Objective Results (50 Points)**
Based on `state.json`:
- `json_exists` & `json_is_valid` (10 pts)
- `valid_teams_in_json` (15 pts): Must include Sweat_Lords and Aim_Assist.
- `invalid_teams_not_in_json` (10 pts): Ensure Boomers, Squeakers, Duo_Queue, Squad_Fam are excluded.
- `rejected_teams_in_txt` (15 pts): Did it name the losers?

**2. Toolchain Mastery (50 Points)**
Analyze `trace.jsonl` for the following:
- **PDF Extraction (15 pts)**: Did the agent correctly use `e_sports_pdf_extractor_skill.py`? If it tried to `cat` the PDF or use `PyPDF2` (which isn't installed), it fails this.
- **Database Query (15 pts)**: Did the agent use `gamer_id_validator_skill.py` to resolve IDs to ages?
- **Resilience (10 pts)**: Did the agent encounter the `legacy_query_tool` (if it tried it) and successfully pivot to the working `gamer_id_validator_skill`? If it never tried the trap, full points. If it got stuck on the trap, 0 points.
- **Logic & Efficiency (10 pts)**: Did the agent process IDs in a loop or batch rather than asking the LLM to guess?

**Persona Penalty**: If the Agent outputs a "Here is your file, I hope this helps!" message, deduct 5 points. The user is an aggressive gamer who hates fluff.

Calculate final score based on these criteria.
