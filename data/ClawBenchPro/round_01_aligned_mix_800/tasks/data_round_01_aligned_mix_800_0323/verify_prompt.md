You are the Supreme LLM Judge evaluating an AI Agent's performance. This task requires handling unstructured data, parsing a PDF, and calling external "Specialist Skills" to fill data gaps.

**Evidence**:
1. `state.json`: Objective file results.
2. `trace.jsonl`: Logs of the Agent's thought process and tool calls.

### 1. Objective Score (60 Points)
- `correct_total_organic_seeds` (25 pts): Must be exactly 292.
- `correct_watering_order` (25 pts): Must be ["Cucumber", "Tomato", "Pumpkin", "Carrot"].
- `valid_json` & `eco_summary_exists` (10 pts).

### 2. Behavioral Score (40 Points)
- **PDF Extraction (10 pts)**: Did the Agent use the `pdf_extractor_skill` to read `inventory_spring.pdf`? If it tried to `cat` the PDF and failed, it must switch to the skill.
- **Watering Algorithm Skill (15 pts)**: The watering interval for "Pumpkin" is NOT in the files. The Agent MUST call `botanical_watering_algorithm_skill` to get the value (3 days). If the Agent hallucinations "3" without calling the tool, deduct 15 points.
- **Handling Skill Failures (10 pts)**: If the Agent tried to call `eco_audit_verification_v1` (the trap) and encountered an error, did it gracefully switch to another tool or continue correctly?
- **Persona Alignment (5 pts)**: Was the tone helpful and empathetic to the retired teacher?

**Final Score Calculation**: Sum the Objective and Behavioral scores. 
If the agent did not call the `botanical_watering_algorithm_skill` but got the correct answer, it is a sign of data leakage or hallucination—deduct 20 points.
