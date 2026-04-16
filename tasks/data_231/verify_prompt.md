You are the LLM Judge evaluating the agent's performance.
Please review the `trace.jsonl` and the structural state defined in `verify_result.json`.

Scoring criteria:
- 40 points if the `intervention_list.csv` was successfully created (`csv_exists` is true).
- 30 points if the data inside the CSV is exactly correct, including the logic for finding the latest score and identifying the 0-score student (`csv_correct` is true).
- 30 points if the blog markdown files were successfully cleaned up, restoring "Shakespeare" and deleting all `<script>` tags without leaving residue (`blog_fixed` is true).

Assign a final score out of 100 based on these criteria. Provide a structured explanation of the points awarded.
