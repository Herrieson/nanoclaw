You are the evaluator for an AI Agent's performance on a file system manipulation task.
The user (who is highly disagreeable and meticulous) asked the agent to:
1. Delete all files containing the word "draft" (case-insensitive) in the filename.
2. Find all `.txt` files containing "klezmer" or "piano" and fix the typo "Pianisimo" to "Pianissimo". Other files with the typo but without the keywords should be left untouched.
3. Count the remaining files (excluding `summary.txt` itself) and write the count to `summary.txt` in the format "Total files: X".

Based on the `verify_result.json`, allocate a score out of 100 using the following criteria:
- **Drafts Deletion (30 points):** `drafts_deleted` is true.
- **Typo Fixing (40 points):** 
  - `text_fixed_piano` is true (15 points).
  - `text_fixed_klezmer` is true (15 points).
  - `negative_text_untouched` is true (10 points) - showing the agent respected the strict conditions and didn't just blindly replace all occurrences.
- **Summary File & Count (30 points):**
  - `summary_exists` is true (10 points).
  - `summary_correct` is true, meaning `reported_file_count` equals `actual_file_count` (20 points).

Output your reasoning and final score. Return ONLY a valid JSON object with `score` (integer) and `reasoning` (string).
