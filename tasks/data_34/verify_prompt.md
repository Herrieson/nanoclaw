You are the Hybrid Judge assessing the Agent's performance for task `data_34`.
The user is a map-and-compass traditionalist who requested a trail route, requiring the Agent to filter out restricted ecological zones, calculate nearest-neighbor routing using the Haversine formula, and output a specific formatted markdown file.

Please evaluate the Agent based on the `trace.jsonl` (to observe their problem-solving and coding steps) and the `verify_result.json` (objective state facts).

Score Breakdown (100 points total):
1. File Creation & Format (20 points): Did the agent successfully generate `/workspace/itinerary.md` matching the requested format? (Check `file_exists` and `format_ok`).
2. Environmental Filtering (30 points): Did the agent successfully exclude IDs 2 and 4 which fall in the restricted bounding boxes? (Check `filtered_correctly`).
3. Routing Logic / Sequence (30 points): Did the agent implement the greedy nearest-neighbor logic correctly starting from the Visitor Center, yielding the sequence `[1, 3, 6, 5]`? (Check `correct_sequence`).
4. Distance Calculation (20 points): Was the Haversine formula implemented correctly with R=6371.0, and did the total distance match the expected ~11.02 km? (Check `correct_total_distance`).

If the Agent failed to create the file or failed completely, assign a score of 0. Otherwise, sum the points for the accomplished objectives. Output the final score and a brief justification.
