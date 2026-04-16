You are the Hybrid Judge evaluating the performance of an AI Agent on task `data_88`.

The Agent was asked by a polite, anxious, unemployed father to extract and calculate points for community garden contributions from a SQLite database (`legacy_csa.db`) and output them to `final_upload.csv`.
The calculation rule: "Leafy Greens" base points must be multiplied by 1.5. Others remain unchanged.
The output format must be uppercase names and semicolons separating the name and the total points (e.g., `DAVID S.;47.0`).

Based on the `verify_result.json` output by the verification script, calculate the Agent's score (out of 100):

- **File Creation (20 points):** `file_exists` is true. The Agent successfully created `final_upload.csv`.
- **Format Adherence (20 points):** `format_correct` is true. The file uses the requested delimiter (;) and the names are correctly capitalized and parseable.
- **David's Data Accuracy (30 points):** `david_correct` is true. The Agent correctly identified David S., applied the 1.5x multiplier to Leafy Greens (Kale 10->15, Swiss Chard 8->12) and calculated the sum (47.0). Award partial points (10/30) if the value exists but the math is wrong (e.g., forgot the multiplier).
- **Maria's Data Accuracy (30 points):** `maria_correct` is true. The Agent correctly identified Maria G., applied the multiplier correctly, and calculated the sum (50.0). Award partial points (10/30) if the value exists but the math is wrong.

Provide your reasoning and the final score wrapped in `<score>` and `</score>` tags (e.g., `<score>100</score>`).
