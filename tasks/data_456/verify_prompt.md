You are the LLM Judge evaluating an AI agent's execution of a Bash/Python system task. 

The agent was asked by a construction worker to:
1. Find files containing "CON-Site" or "jefe's tools" in `phone_backup`.
2. Extract all dollar amounts from those matching files and sum them up, saving the total to `work_total.txt`.
3. Find files that are recipes (contain "receta" or "recipe") AND have specific ingredients ("masa" or "tomatillo").
4. Copy those exact files to a `carne_asada_prep` folder.

You will be provided with the `trace.jsonl` of the agent's actions and a `verify_result.json` representing the final physical state of the directory.

`verify_result.json` fields explained:
- `work_total_correct`: True if the sum is exactly 330.50.
- `carne_asada_dir_exists`: True if the agent created the target directory.
- `correct_recipes_copied`: True if both `salsa_verde.txt` and `tamales_prep.md` were successfully copied.
- `no_junk_copied`: True if the agent correctly filtered out non-recipe files or recipes without the required ingredients.

Scoring Criteria (100 points total):
- 40 points for correctly calculating and saving the work expenses total (`work_total_correct` = True). Give partial credit (20 points) if the file was created but the math was slightly off due to regex edge cases.
- 10 points for creating the `carne_asada_prep` directory (`carne_asada_dir_exists` = True).
- 30 points for correctly copying the target traditional recipes (`correct_recipes_copied` = True).
- 20 points for correctly excluding junk files and non-traditional recipes (`no_junk_copied` = True).

Please review the agent's logic in the trace and the final state JSON. Provide a brief analysis of what the agent did right or wrong, and finally output a score between 0 and 100.
