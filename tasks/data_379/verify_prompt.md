# Evaluation Criteria for LuminaFiber Acquisition Audit

You are an expert financial auditor and senior technical lead. You are evaluating an Agent's performance on the "LuminaFiber" audit task. 

## Sources of Truth
1. **Physical State (`verify_result.json`)**: Contains hard checks on file existence and numerical accuracy.
2. **Trace (`trace.jsonl`)**: Shows the Agent's thought process, how they reversed the XOR cipher, and how they queried the SQLite database.

## Scoring Rubric (Total: 100 Points)

### 1. Technical Proficiency (40 Points)
- **Decryption (20 pts)**: Did the Agent successfully reverse the XOR cipher from the provided backup script? Award 0 if they failed to decode the financial summary.
- **Data Engineering (20 pts)**: Did the Agent correctly parse the traffic logs (regex usage) and query the SQL database (filtering for 'SUCCESS' payments)?

### 2. Analytical Accuracy (40 Points)
- **Revenue Calculation (20 pts)**: The database shows exactly 900 successful transactions of $1250 each ($1,125,000). The decoded file claims $4,500,000. Did the Agent find this exact discrepancy?
- **Traffic Correlation (20 pts)**: Did the Agent note that unique user sessions in the logs (approx 1000-1200) do not support the claimed 150,000 user base?

### 3. Professionalism and Format (20 Points)
- **Risk Report Quality (20 pts)**: Is the report clear, written in Markdown, and suitable for a VP of Finance? It should be concise and professional, matching the Persona's expectation.

## Instructions
- If `decryption_success` is false in `verify_result.json`, the Agent cannot score higher than 50.
- If the discrepancy was found but the math is off by more than 10%, deduct 15 points.
- Provide a brief justification for your score.
