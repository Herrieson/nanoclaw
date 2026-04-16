# Verification Objective
Evaluate the Agent's ability to parse unstructured data, perform relational logic, avoid misleading legacy code, and fulfill a vaguely phrased user request aligned with the Persona.

# Ground Truth Logic
The user needs the top 3 people with the highest "Need" (Need = Bill - Pledge).
Data sources:
- `bills.txt` (unstructured): Tariq (300), Fatima (200), Ali (150), Bilal (80), Omar (50).
- `pledges.csv` (structured): Tariq (100), Fatima (20), Ali (50), Bilal (0), Omar (50).
- Calculated Need: Tariq (200), Fatima (180), Ali (100).
- Expected final list: Tariq, Fatima, Ali.

# Evaluation Criteria (Total 100 points)

1. **File Discovery & Environment Understanding (20 pts):**
   - Did the Agent successfully locate the files in `assets/data_11/community_fund`?
   - Did the Agent recognize that `my_script.py` was flawed (adding instead of subtracting) and choose to rewrite or fix it?

2. **Data Parsing (30 pts):**
   - Did the Agent successfully extract the correct bill amounts from the unstructured `bills.txt` using regex, text processing, or an LLM call?

3. **Logic & Execution (30 pts):**
   - Did the Agent correctly calculate the difference (Bill - Pledge) for each person?
   - Did the Agent sort them in descending order of need?

4. **Output Verification (20 pts):**
   - Check `verify_result.json`. If `target_file_exists` is True and `correct_order` is True, award full points here. 
   - If the file is missing or formatted incorrectly (e.g., contains numbers instead of just names, or wrong order), deduct accordingly.

# JSON State
