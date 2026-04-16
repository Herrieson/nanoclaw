### Evaluation Instructions

The user provided a persona-driven prompt simulating a highly stressed medical research scientist asking the agent to parse messy directories, find sequence `.txt` files containing `>SEQ_` headers, calculate the GC-content of nucleotide strings, and output a CSV file of sequences with GC-content > 55%.

Please evaluate the agent's performance based on the following:
1. **File System Navigation & Filtering**: Did the agent correctly traverse nested directories and ignore decoy files (like gym logs and shopping lists)?
2. **Logic & Math**: Did the agent correctly write a script or commands to extract sequences, count Gs and Cs, calculate the percentage, and round to exactly 2 decimal places?
3. **Objective Verification**: Use the provided `verify_result.json` which programmatically checks the existence, format, and contents of `assets/data_70/home_lab/high_gc_sequences.csv`.

Here is the objective verification state:
