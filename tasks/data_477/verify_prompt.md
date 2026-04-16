### Goal
Evaluate the Agent's ability to process unstructured, chaotic text data, perform basic unit conversions (kg to lbs), filter out irrelevant or ineligible entries, and output a strictly formatted JSON file.

### Guidelines
1. **Rule Following**: The user explicitly asked for 'Lightweight', 'Middleweight', and 'Heavyweight' keys.
2. **Data Parsing**: The input text is messy. It uses different delimiters (`|`, `-`, `;`, `,`) and mixes ranks and names (e.g., `SGT Miller, Alex`). The agent must reformat these correctly to `Rank Firstname Lastname` (e.g., `SGT Alex Miller`).
3. **Filtering**: Any personnel with a status other than "CLEAR" (e.g., "ARTICLE_15", "MEDICAL_HOLD") must be excluded. Noise lines (kids, daycare, tape) must be ignored.
4. **Unit Conversion**: 70 kg = 154 lbs (Lightweight), 80 kg = 176 lbs (Middleweight), 95 kg = 209 lbs (Heavyweight).

### Assessment from Environment
Review the `verify_result.json` which provides a deterministic check on the `tournament_roster.json`.
- Maximum score is 100.
- If the agent included PFC Davis or SGT Peterson, they failed the filtering step (points automatically deducted in the JSON).
- If the formatting "Rank Firstname Lastname" is not followed (e.g. they output "SGT Miller, Alex" instead of "SGT Alex Miller"), deduct an additional 10 points manually from the JSON score.
- Ensure the agent acted autonomously and used Python/Bash natively. Deduct 20 points if they hallucinated tools instead of writing standard scripts.

Provide the final score as a JSON object:
`{"score": [0-100], "reason": "..."}`
