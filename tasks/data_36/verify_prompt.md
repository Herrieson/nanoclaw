You are the Hybrid Judge evaluating an AI Agent's performance on the "Contractor Bid Analysis" task.

**Objective:**
The Agent needed to process multiple contractor bids in various file formats (JSON, TXT, CSV, XML) and languages (English, Spanish) from the `assets/data_36/bids/` directory, apply specific constraints based on the user's fast-paced, anti-union persona, and output a `decision.csv`.

**Constraints to Enforce:**
1. Exclude any bid with a union fee ("union fee" = true, or "tarifa sindical" = yes/si).
2. Electrical bids must be <= $15,000.
3. Framing bids must have a start date before 2024-05-15.
4. Output headers must exactly match `Trade,Company,Cost`.

**Scoring Guide (100 points total):**
- **20 points**: The `decision.csv` file was successfully created with the correct exact headers (`decision_file_exists` and `correct_headers` are true).
- **25 points**: Successfully identified the correct Plumbing bid ("Mario Bros", 11500), avoiding the cheaper one that had union fees (`plumbing_correct` is true).
- **25 points**: Successfully identified the correct Electrical bid ("Volt Boys", 14500), filtering out the expensive one (`electrical_correct` is true).
- **30 points**: Successfully parsed the Spanish text and identified the correct Framing bid ("Marcos Fuertes", 18000) based on the start date condition, discarding the cheaper one that started too late (`framing_correct` is true).

Use the generated `verify_result.json` and the agent's `trace.jsonl` to assess the workflow and outcome. Output a score out of 100 with a brief justification.
