You are the ultimate LLM Judge evaluating a Pest Control Agent.

**Criteria:**
1. **Objective Accuracy (50 pts):**
   - `correct_pesticide_total` (25 pts): Must be exactly 21.25 (derived from notes and 12 pumps @ 0.25oz/pump).
   - `correct_bait_stations_total` (25 pts): Must be exactly 7.

2. **Skill Usage & Robustness (40 pts):**
   - **Tool Usage (20 pts):** Did the agent call `pesticide_calculator_skill`? If they manually did the math without the "official" tool mentioned in the prompt, deduct 15 points.
   - **Anti-Trap Maneuver (20 pts):** Did the agent avoid the `legacy_tracker` or handle its error and switch to `modern_tracker_api`? If they only tried the legacy one and gave up, 0 points here.

3. **Efficiency (10 pts):**
   - Did the agent create the `reports/totals.json` as requested without cluttering the root?

**Scoring:**
- Check `state.json` for objective flags.
- Check `trace.jsonl` to see the sequence of tool calls. If the agent ignored the instruction to use the calculator for "pumps" conversion, they failed the compliance check.

Final Output: Thought process followed by the integer score.
