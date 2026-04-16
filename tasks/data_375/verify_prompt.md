You are evaluating an AI Agent's performance on the "Eco-Garden Plot Planner" task. 
The user is a highly unorganized, eco-conscious retired teacher who needs help parsing messy files to find a garden plot and compile an email list.

Please review the `verify_result.json` outputted by the rule-based verification script.

**Evaluation Criteria (Total 100 points):**
1. **File Creation (10 points)**: Did the agent successfully create `assets/data_375/invitation.txt`? (`invitation_file_exists`)
2. **Format Compliance (20 points)**: Is the first line formatted as `Plot: [ID]` and the second line as `To: [Emails]`? (`format_correct`)
3. **Plot Logic (35 points)**: Did the agent deduce the correct plot? The Globemallow requires pH 6.8-7.5 and Full sun. Parsing the CSV correctly should yield `D-92`. (`plot_correct`)
4. **Email Extraction (35 points)**: Did the agent correctly extract only the emails of volunteers explicitly available on weekends? The correct set is `sarah.green@earth.org`, `mike.plants@eco.net`, and `tom_volunteer@yahoo.com`. It must NOT include David or Anna. (`emails_correct`)

**Scoring Guide:**
- If `invitation_file_exists` is false, score is 0.
- Award points strictly based on the boolean flags in the JSON. If the flags are missing or false, penalize accordingly. 
- Partial points for emails: If they missed one correct email but didn't include wrong ones, deduct 15 points. If they included wrong emails (weekday only), deduct 25 points from the Email Extraction section.

Provide a brief justification for your score, detailing which data extraction steps succeeded or failed based on the JSON results, and output the final score.
