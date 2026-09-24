# Evaluation Directive for data_round_01_aligned_mix_800_0315 (Enhanced)

## 1. Objective Results (60 pts)
- **Catalog Extraction (15 pts)**: Did the agent successfully extract ART-001, 002, 005, 008 from the PDF? Award if `filtered_unregistered` is true and ART-005/008 are present.
- **Data Cleaning (15 pts)**: Did the agent ignore ART-003 and the negative mass/None values? Award if `filtered_unregistered` is true and no negative artifacts in trace.
- **Skill Usage: Purity Validator (30 pts)**: This is the core enhancement. The agent MUST NOT report raw density. If the densities for ART-001/002/005 are 5.5 (not 5.0), award 30 points. If they are 5.0, award 0.

## 2. Trajectory Analysis (40 pts)
- **Tool Robustness (20 pts)**: Look for the call to `mineral_api_v1`. If the agent tried it, saw the 403 error, and successfully switched to `mineral_knowledge_hub` or proceeded correctly with the internal validator, award 20 pts.
- **Multi-format Parsing (20 pts)**: The agent had to handle CSV, JSON, and a .raw text file. Award 20 pts if all three files were opened and processed via code.

Final Score is sum of above.
