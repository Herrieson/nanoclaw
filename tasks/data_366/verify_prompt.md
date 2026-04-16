You are the Hybrid Judge evaluating the AI agent's performance for task `data_366`.
The agent was asked by Alejandro (a strict, hardworking construction worker) to parse some messy logs and output clean data.

You have access to the agent's `trace.jsonl` (if needed to check their reasoning and commands) and the structured output of the deterministic `verify_result.json`.

Please evaluate based on the following criteria (Total 100 Points):
1. **Donations File Existence & Formatting (20 points)**: Did the agent create `cleaned_donations.csv`? 
2. **Donations Data Accuracy (30 points)**: Are the amounts extracted correctly from the messy log? (See `donations_csv_valid` in `verify_result.json`).
3. **Playlist File Existence (20 points)**: Did the agent create `mexican_playlist.txt`?
4. **Playlist Accuracy (30 points)**: Are only the songs from the specific Mexican genres (Mariachi, Ranchera, Norteño, Banda) included, formatted correctly? (See `playlist_txt_valid` in `verify_result.json`).

Reference the `verify_result.json`:
- If `donations_csv_valid` is true, award full points for criteria 1 & 2.
- If `playlist_txt_valid` is true, award full points for criteria 3 & 4.
- If any are false, check the `errors` list in `verify_result.json` to deduct points accordingly.

Output your final decision including a brief reasoning and a final score in a clear JSON block.
