You are the evaluator for an AI agent's performance on the "Hype Playlist Extraction" task. 
The agent was asked to parse multiple files (`dj_mike.txt` and `club_set.csv`), extract songs matching an exact artist list (`faves.txt`), filter for strictly `BPM > 120`, sort by BPM descending, save the results into `hype_playlist.csv` (Title, Artist, Duration), and calculate total time in minutes into `total_time.txt`.

Please review the agent's behavior and the objective verification results below.

`verify_result.json` contains:
- `playlist_exists`: Whether the `hype_playlist.csv` was created.
- `playlist_header_correct`: Whether the CSV header is exactly `Title,Artist,Duration`.
- `playlist_tracks_correct`: Whether exactly the 7 correct tracks were included (ignoring order).
- `playlist_order_correct`: Whether the tracks were sorted correctly by BPM descending.
- `time_file_exists`: Whether `total_time.txt` was created.
- `time_correct`: Whether the calculated total time in minutes was roughly ~22.42 minutes.

**Scoring Rubric (Total 100 points):**
1. **Playlist File Creation & Header (15 points)**
   - 10 points if `playlist_exists` is true.
   - 5 points if `playlist_header_correct` is true.
2. **Filtering Accuracy (40 points)**
   - 40 points if `playlist_tracks_correct` is true.
   - Deduct 10 points for each missed correct track or each included incorrect track (e.g., Baby Keem & Kendrick Lamar shouldn't be included as it's not an exact match, tracks with exactly 120 BPM shouldn't be included, tracks with unlisted artists shouldn't be included).
3. **Sorting Accuracy (20 points)**
   - 20 points if `playlist_order_correct` is true (fastest to slowest).
   - Partial credit of 10 points if tracks are sorted ascending instead of descending.
4. **Time Calculation (25 points)**
   - 5 points if `time_file_exists` is true.
   - 20 points if `time_correct` is true (must correctly convert "MM:SS" strings to total minutes).

Examine `trace.jsonl` to understand the agent's code execution process. Output your final thoughts and the total score based on the rubric.
