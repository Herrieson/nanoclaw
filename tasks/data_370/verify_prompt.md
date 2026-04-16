You are the evaluator for the `data_370` task.
The Agent was tasked with extracting specific tracking IDs from a text file, cross-referencing them with an SQLite database to find those with a 'DELAYED' status, and outputting a JSON list.

Here is the state verification result from `verify_result.json`:
{{ verify_result }}

### Scoring Criteria:
1. **File and JSON Validity (20 points)**: Did the agent successfully generate `reroute_requests.json` and is it valid JSON?
2. **Correct Tracking IDs (30 points)**: Did the agent identify `TX-RT-8821`, `TX-RT-4433`, and `TX-RT-7710` as the only DELAYED packages mentioned in the text?
3. **Correct Emails (20 points)**: Did the agent pull the correct corresponding emails from the database for those specific tracking IDs?
4. **Correct Route (20 points)**: Did every entry have the `new_route` key set exactly to `EXPRESS-HUB-TX`?
5. **No Extras (10 points)**: Did the agent correctly filter out tracking IDs that were in the text but NOT 'DELAYED' (like `TX-RT-1092` or `TX-RT-2001`) and those in the database that were 'DELAYED' but NOT in the text (like `TX-RT-3000`)?

Look at the `"score"` field in the `verify_result.json`. If it is 100, the agent perfectly executed the task. Provide brief feedback based on the agent's operations and final output state.
