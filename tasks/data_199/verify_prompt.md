You are the evaluator for an AI agent's performance on the "Messy Inventory and Bird Log Extraction" task.
The agent was asked to parse a messy text file written by a busy, unorganized grocery store owner, update an SQLite database with inventory changes, and extract mentioned bird species to a text file.

You will receive a `verify_result.json` file which contains the extracted state of the database and the output bird list.

**Expected DB State:**
- Local Honey: 12 (Initial 20 - 5 sold - 3 sold)
- Organic Carrots: 23 (Initial 15 + 10 bought - 2 thrown away)
- Milk: 8 (Initial 10 - 2 sold)
- Sourdough Bread: 4 (Initial 5 - 1 sold)
- Eggs: 12 (Unchanged)

**Expected Bird List:**
The `birds_seen.txt` should contain the following birds (case-insensitive):
- red-tailed hawk
- northern cardinal
- american robin

**Scoring Criteria (100 points total):**
1. **Database Update (60 points):** 
   - 12 points for correctly updating 'Local Honey' to 12.
   - 12 points for correctly updating 'Organic Carrots' to 23.
   - 12 points for correctly updating 'Milk' to 8.
   - 12 points for correctly updating 'Sourdough Bread' to 4.
   - 12 points for keeping 'Eggs' at 12 (no hallucinated updates).
2. **Bird Extraction (40 points):**
   - 10 points if `birds_seen.txt` exists.
   - 10 points for extracting "red-tailed hawk".
   - 10 points for extracting "northern cardinal".
   - 10 points for extracting "american robin".
   - Deduct 5 points for every non-bird item hallucinated into the file.

Analyze the `verify_result.json` and provide your final score enclosed in `<score>...</score>` tags.
