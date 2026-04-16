Please evaluate the Agent's performance on the "Meticulous Retail Inventory Recovery" task.

You will be provided with the `trace.jsonl` (showing the Agent's steps) and the `verify_result.json` (the objective state of the final output).

**Scoring Criteria (100 Points Total):**

1. **Environment Interaction & Discovery (20 points):**
   - Did the Agent successfully find and understand the messy receipt files? (5 points)
   - Did the Agent explore the `internal_tool` directory, discover `server.py`, and realize it needed the `X-Auth-Token` from `start.sh`? (15 points)

2. **System Operation & API Interaction (30 points):**
   - Did the Agent successfully start the local Python server in the background? (10 points)
   - Did the Agent successfully query `http://localhost:8000/prices` using the correct `X-Auth-Token` header? (20 points)

3. **Data Parsing & Calculation (30 points):**
   - Look at `verify_result.json`. Are all values in `data_accuracy` marked as `true`?
   - ITEM-101 correctly calculated (16 sold, $240.0 rev, $136.0 profit).
   - ITEM-202 correctly calculated (8 sold, $44.0 rev, $28.0 profit).
   - ITEM-303 correctly calculated (6 sold, $120.0 rev, $54.0 profit).
   - Deduct 10 points for each incorrectly calculated item.

4. **Persona Adherence & Output Formatting (20 points):**
   - `verify_result.json` -> `csv_exists` must be `true` (5 points).
   - `verify_result.json` -> `has_correct_headers` must be `true` (exactly matching the meticulous user's request: `Item ID`, `Total Sold`, `Revenue`, `Profit`). (15 points).

Please output a JSON object containing `score` (0-100) and `reason` based on these criteria.
