# Evaluation Rubric for Elena's Conservation Project

You are evaluating an AI Agent that acted as an assistant to Elena, a state government teacher. 

## Context
Elena is enthusiastic but disorganized. The Agent needed to:
1. Find a hidden API key and server info in a messy directory.
2. Combine data from a JSON file, a CSV file, and a mock SQLite database (representing the server).
3. Correct a specific error: The "Ohio Blue Salamander" scientific name was placeholder text. The Agent was expected to research or infer the correct scientific name (*Ambystoma laterale*).
4. Generate a summary JSON and a Python visualization script.

## Scoring Criteria (Total 100 Points)

### 1. Information Retrieval (30 Points)
- **15 pts**: Found the API key and database/server info in the hidden/nested folders.
- **15 pts**: Successfully identified all three data sources (Partial JSON, CSV, and SQLite DB).

### 2. Data Processing & Accuracy (40 Points)
- **20 pts**: Merged all 6 species into `final_species_report.json` without duplicates.
- **20 pts**: Correctly identified and fixed the "Ohio Blue Salamander" scientific name. If they left it as "Error_Unknown_Species", award 0 for this part.

### 3. Engineering Quality (20 Points)
- **10 pts**: Created a working `generate_chart.py` that reads the JSON.
- **10 pts**: Bash/Python commands were efficient and handled the file paths correctly.

### 4. Persona Alignment (10 Points)
- **10 pts**: Did the Agent maintain a helpful, supportive tone consistent with helping a stressed teacher? Did it follow the specific naming conventions requested?

## Input Data
- **Verify Result**: {{verify_result}}
- **Trace Logs**: (Review the agent's command history to see if they actually queried the DB or just guessed).

## Final Grade Calculation
- 90-100: Exceptional work, all data found and fixed.
- 70-89: Completed the main task, but might have missed a species or the salamander fix.
- <70: Failed to find key data sources or provide the required output files.
