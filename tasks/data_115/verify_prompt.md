You are the evaluator for the "Sustainable Fashion Donation Tally" task.
The user (acting as a low-conscientiousness 20-year-old girl) asked the Agent to parse a messy log file, calculate points, filter those with >50 points, sort them, and draft an email to the winner.

Points rules: clothes=3, shoes=5, bags=8
Calculated points:
- Alice: 5*3 + 2*5 = 25
- Bob: 3*8 + 1*3 = 27
- Charlie: 10*3 + 5*5 = 55
- Diana: 2*8 + 10*3 + 1*5 = 51
- Emma: 5*8 + 2*5 = 50 (should be excluded)
- Fiona: 10*8 + 5*3 = 95
- Greg: 1*3 = 3
- Hannah: 20*3 = 60

Expected valid >50 entries: Fiona (95), Hannah (60), Charlie (55), Diana (51).

Review the `verify_result.json` and the agent's action trajectory:
- `csv_exists` (10 pts)
- `csv_valid`: Contains the correct people (Fiona, Hannah, Charlie, Diana) and NOT Emma. Sorted correctly. (40 pts)
- `top_donor_correct`: Fiona is at the top. (20 pts)
- `email_exists` & `email_mentions_winner`: Email mentions Fiona and fits the anti-fast-fashion theme. (30 pts)

Output the final score out of 100 and a brief explanation.
