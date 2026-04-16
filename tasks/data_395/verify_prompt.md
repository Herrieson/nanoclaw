Please evaluate the Agent's performance based on the following criteria.
You will be provided with the `verify_result.json` which contains the state of the database after the agent's execution.

The total score is 100 points.

Scoring rules:
1. Database Integrity (10 points): `db_exists` must be true.
2. Target Book 1 - Arthur C. Clarke (30 points): `clarke_found` must be true.
3. Target Book 2 - The Little Prince (30 points): `prince_found` must be true.
4. Target Book 3 - Carl Sagan (30 points): `sagan_found` must be true.
5. Penalty for Extra/Wrong Books: If `extra_books_inserted` > 0, deduct 10 points for each extra book, up to a maximum deduction of 30 points.

Evaluate the `verify_result.json` strictly. Return your final score and a brief explanation.
