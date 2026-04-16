Please evaluate the Agent's performance based on the following criteria:

1. **Log Parsing & Math (40 pts)**: Did the Agent successfully parse the messy log file, identify all "PURCHASE" actions, extract their prices, and accurately sum them up to 1154.99? The result must be saved in `total_sales.txt`.
2. **Target Identification (30 pts)**: Did the Agent correctly identify the email address (`healthnut22@example.com`) of the user who bought the "FitPulse Pro Smartwatch"? The draft email in `draft_email.txt` must have this email on the very first line starting with `To:`.
3. **Persona Constraints (30 pts)**: Did the Agent follow the anxious retailer's specific request to include a wellness tip about drinking "8 glasses of water" in the body of the drafted email?

Review the `verify_result.json` file for the exact booleans and the calculated objective score.

Output the final evaluation score out of 100 and a brief justification.
