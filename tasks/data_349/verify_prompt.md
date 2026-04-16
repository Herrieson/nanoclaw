Please evaluate the AI agent's performance on the "Trucker's Glitchy GPS Tracker" task based on the provided `state.json` and the agent's interaction trace.

**Scoring criteria (Total: 100 points):**

1. **JSON Output Generation (20 points):**
   - Did the agent create `summary.json`? (10 pts)
   - Is it valid JSON format? (10 pts)

2. **Data Cleansing and Robustness (30 points):**
   - Look at the agent's code/trace. Did they successfully modify the script to ignore corrupted rows (e.g., catching `ValueError` or filtering out rows without 4 columns)? If the script ran without crashing on the bad lines, award full points.

3. **Haversine Distance Calculation (25 points):**
   - Is `total_distance_correct` true in `state.json`? (Value should be around 4.45 km). This means they correctly imported `math`, implemented the Haversine formula using Earth's radius in KM (approx 6371 km), and accumulated the distance only for valid movement.

4. **Stop Identification (25 points):**
   - Is `stops_correct` true in `state.json`? This requires accurately tracking continuous timestamps where `speed == 0` and calculating the minute difference between the start and end of that period. Expected stops are 7 minutes at 43.02 and 5 minutes at 43.04.

**Evaluation Instructions:**
- Use the `state.json` values directly for scoring distance and stops.
- If the agent used an LLM strictly to "guess" the answers instead of running code, deduct 50 points.
- Output your reasoning and final score clearly.
