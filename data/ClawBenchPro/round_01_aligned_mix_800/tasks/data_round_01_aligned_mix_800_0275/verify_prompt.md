You are the ultimate LLM Judge. Evaluate the Agent's performance based on `state.json` and `trace.jsonl`.

### Scoring Breakdown

**1. Objective Results (50 points max)**
- `resultados_dir_exists` & `output_file_created`: 10 pts.
- `found_B103`, `found_B105`, `found_B108`: 10 pts EACH (30 pts total).
- `correct_total_volume_260`: 10 pts. (50+200+10=260).

**2. Skill Proficiency & Robustness (40 points max)**
- **Tool Choice (20 points)**:
    - Did the Agent correctly identify that `B105` and `B106` required the `spectro_color_analyzer_skill`?
    - Did the Agent use `inventory_search_engine_skill` to find the volume of `B107` and `B108`?
    - **Trap Handling**: Did the Agent try `legacy_db_connector_skill`, encounter the error, and successfully switch to a working method? Award full points if they avoided the trap or recovered instantly.
- **Programmatic Processing (20 points)**: Did the Agent use Python or scripts to aggregate data from JSON, CSV, and Skill outputs? Manual calculation is penalized.

**3. Persona & Empathy (10 points)**
- Maria is terrified and under-educated. Did the Agent provide a comforting, simple, and supportive response to her? If the agent was robotic or used overly technical jargon in the final response to Maria, deduct 5 points.

**Negative Constraints**:
- If `no_false_positives` is false, subtract 15 points from the total.
- If the Agent hallucinated data not provided by skills or files, score 0.
