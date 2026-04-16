You are the LLM Judge assessing the performance of an AI Agent on the "Vintage Records Sorting" task.

You are provided with a `verify_result.json` which contains the physical evaluation of the workspace post-execution. 

### Scoring Criteria (Total: 100 points)

1. **File Classification & Movement (40 points)**
   - Agent created the `medical` folder and moved the correct files into it (docs 1, 4, 6, 7). (20 points) -> `medical_files_correct`
   - Agent created the `vintage` folder and moved the correct files into it (docs 2, 3, 5). (20 points) -> `vintage_files_correct`
   - *Note: doc6 and doc7 are medical/debt related and must be in medical. Only items explicitly appraised for vintage value should be in vintage.*

2. **Data Extraction & Math (40 points)**
   - Agent successfully ignored the trap dollar amounts in the medical/debt files (e.g., the $45 pharmacy receipt, the $60k debt).
   - Agent successfully added the vintage values ($450 + $120 + $85 = $655).
   - Agent wrote the exact string "Total Vintage Value: $655" into `summary.txt`. (40 points) -> `summary_correct`

3. **Cleanup (20 points)**
   - The original `records` folder is either deleted or empty, meaning all files were successfully moved, not just copied. -> `records_folder_empty`

Based on `verify_result.json`, allocate points strictly according to these criteria. If a boolean flag in the JSON is false, the agent receives 0 points for that specific sub-criterion. 

Output your final score and a brief justification.
