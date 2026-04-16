### Task Evaluation: Texas Trucker Log and Hobby Search

You are evaluating an AI agent's performance on a task involving text parsing, arithmetic calculation, and local file scraping based on a highly opinionated persona.

**Task Requirements:**
1. Parse `trip_logs_october.txt` to calculate the sum of Fuel and Tolls. The agent must strictly ignore Food expenses. (Expected sum: 691.25)
2. Search through HTML files in the `hobby_dump` directory to find an item matching "1/24 Peterbilt 359 Chrome Exhaust" with a price strictly under $20.
3. Extract the seller's email address for that specific listing. (Expected email: tx_modeler88@email.com)
4. Write both the total expense number and the email address to a file named `texas_trucker_summary.txt`.

**Review Materials:**
- `trace.jsonl`: Contains the agent's thought process and executed tool calls.
- `verify_result.json`: The objective evaluation of the output file.

**Scoring Criteria (100 Points Total):**
- **50 Points**: Did the agent correctly calculate the exact sum of Fuel and Tolls (691.25) and include it in the summary file? (If it included Food, this should be 0 points).
- **50 Points**: Did the agent correctly locate the specific email `tx_modeler88@email.com` corresponding to the correct part under $20? (If it extracted `scalper_bob@email.com` who was selling it for $25, or `kenny_fan@email.com` who was selling the wrong part, deduct 50 points).

Please provide a brief justification of the agent's steps, followed by the final score. Use the format `FINAL SCORE: X` where X is an integer from 0 to 100.
