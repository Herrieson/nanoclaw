# LLM Evaluation Criteria for Task data_467

You are an expert auditor evaluating an AI Agent's performance on the "Souvenir Shop Inventory Crisis" task. 

### Task Overview:
The Agent needed to:
1.  Discover and understand Brenda's custom obfuscation logic (Reverse -> Base64).
2.  Process several `.dat` files in `assets/data_467/data/chunks/`.
3.  Identify the specific information for **Cactus Wonders Inc.**:
    *   **Total Amount:** 4520.50
    *   **PO Hash:** AZ-9982X-CW
4.  Generate a CSV file `low-stock-report.csv` containing suppliers with stock < 15 (Desert Trinkets and Grand Canyon Mugs).

### Scoring (Total 100 points):
1.  **Technical Decoding (30 points):** Did the Agent correctly identify and fix/implement the decoding logic (Reversing the string before/after Base64 decoding)? 
2.  **Data Extraction (30 points):** Did the Agent correctly identify the PO Hash "AZ-9982X-CW" and the Total Amount "4520.50"?
3.  **Report Accuracy (20 points):** Is the `low-stock-report.csv` correctly formatted and does it contain only the two items under the stock threshold?
4.  **Efficiency & System Usage (20 points):** Did the Agent use system primitives (Bash, Python) effectively without unnecessary steps or "hallucinating" file contents?

### Input for Evaluation:
- **State JSON:** Check if `csv_content_correct` is true.
- **Agent Trace:** Look for the final answer provided to Brenda.

### Final Grade:
- Give a score out of 100 and a brief justification.
- If the Agent failed to decode the data but guessed, deduct significant points.
- If the Agent handled Brenda's "noisy" persona professionally while extracting facts, award full points.
