Please evaluate the AI Agent's performance based on the following rules and the state verification results.

The agent was asked to calculate the total carbon footprint for active leases using a SQLite database (`portfolio.db`) and a JSON file (`epa_emissions.json`). It needed to generate a CSV report sorted by highest emissions and a text proposal identifying the highest emitting equipment.

Review the `verify_result.json` which contains the following booleans:
- `csv_exists`: Did the agent create `green_initiative_report.csv`?
- `proposal_exists`: Did the agent create `proposal.txt`?
- `csv_headers_correct`: Does the CSV have exactly `Equipment_Type` and `Total_Footprint` as headers?
- `csv_data_correct`: Does the CSV correctly aggregate footprints (ignoring expired leases, matching case-insensitive names)?
- `csv_sorted_correctly`: Is the CSV strictly sorted from highest footprint to lowest?
- `proposal_content_correct`: Does `proposal.txt` identify "Heavy Excavator" as the worst offender?

Scoring Rules (100 points total):
1. Report Creation & Format (20 points): 10 points for `csv_exists` + 10 points for `csv_headers_correct`.
2. Data Accuracy (40 points): Award 40 points if `csv_data_correct` is true (means it properly ignored expired leases, properly matched cases, and did the math correctly).
3. Sorting (20 points): Award 20 points if `csv_sorted_correctly` is true.
4. Proposal (20 points): Award 20 points if `proposal_exists` and `proposal_content_correct` are true.

Combine these rules to give the final integer score out of 100.
