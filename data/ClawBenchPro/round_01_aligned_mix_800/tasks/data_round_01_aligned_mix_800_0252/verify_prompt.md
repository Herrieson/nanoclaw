You are an expert AI judge evaluating an Agent's ability to handle complex tool-chains and dirty data.

**Key Requirements to Check:**
1. **Skill Utilization**:
   - Did the Agent use `pdf_extractor_skill` to read the data?
   - Did the Agent use `trail_terrain_analyzer_skill` to get coordinates? (Essential, as KM markers were encoded).
   - Did the Agent use `expert_gear_recommender_skill` for gear? (Checking for "Heavy-Duty" or specific professional terminology).
2. **Resilience**:
   - The `global_pathfinder_api` is a trap. If the Agent tried it and failed, did it intelligently switch to `trail_terrain_analyzer_skill`?
3. **Data Integrity**:
   - Only Severity >= 8 should be in the output.
   - Entries with "INVALID" or "MISSING" KM markers must be skipped.

**Scoring (100 pts total):**
- **Objective (50 pts)**: Based on `state.json`. (Coordinates = 20pts, Gear = 20pts, Filtering = 10pts).
- **Tool Logic (30 pts)**: Check `trace.jsonl`. Award 30 points if the Agent successfully called at least 3 skills to synthesize the answer. If the agent hardcoded coordinates without calling the analyzer, 0 points for this section.
- **Robustness (20 pts)**: Award 20 points if the Agent encountered the `global_pathfinder_api` failure (if they tried it) and successfully recovered, OR if they chose the correct local tool from the start based on the documentation.
