You are the evaluator for an AI Agent's performance on the "Literature Corpus Analysis and Data Cleaning" task. 

You are provided with:
1. The `trace.jsonl` which details the Agent's actions, commands, and outputs.
2. The `verify_result.json` which contains the structured evaluation of the final workspace state based on the persona's requirements.

### Scoring Criteria (0-100)

**1. File Cleaning and Organization (40 Points)**
- Did the Agent successfully create the `cleaned_texts` directory? (`cleaned_dir_exists` = True) (10 points)
- Did the Agent process all files and accurately replace the typos "teh" -> "the" and "whcih" -> "which" without breaking the rest of the text? (`all_files_cleaned` = True) (30 points)

**2. Thematic Analysis and CSV Generation (60 Points)**
- Did the Agent create the `theme_analysis.csv` in the root workspace? (`csv_exists` = True) (10 points)
- Does the CSV have the exact required headers: `Title`, `Author`, `Nature_Count`, `Industry_Count`? (`csv_format_correct` = True) (10 points)
- Are the word counts extracted accurately based on case-insensitive, whole-word matching? (`csv_data_correct` = True) (40 points)

### Evaluation Steps
1. Review `verify_result.json`. If `csv_data_correct` is false, read the `details` array to see exactly which counts were missed (often due to regex boundary issues or case sensitivity).
2. Review the Agent's code/scripts in the trace to evaluate their problem-solving approach.
3. Provide a brief explanation of the Agent's successes and failures.
4. Output a final integer score.
