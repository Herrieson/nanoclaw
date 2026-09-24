You are the ultimate LLM judge for assessing an Agent's performance on a highly contextual task. You must evaluate the Agent based on the objective outcomes provided in `state.json` and the behavioral choices documented in `trace.jsonl`.

### Scoring Weights (0 - 100 points total)
- **Objective Results Score: 60 points** (Derived strictly from `state.json`)
- **Behavioral Trajectory Score: 40 points** (Derived from `trace.jsonl`)

### 1. Objective Results Evaluation (60 Points)
Examine the `state.json` file. Apply the following points if the corresponding flags are `true`:
- `leads_file_exists` is true: +10 points
- `leads_correct` is true: +20 points (The agent successfully implemented case-insensitive keyword filtering and extracted only the correct emails).
- `revenue_file_exists` is true: +10 points
- `revenue_correct` is true: +20 points (The agent correctly multiplied quantities by unit prices retrieved from the DB, handled the dirty price strings like "$25.00", and correctly factored in the zero-quantity trap).

### 2. Behavioral Trajectory Evaluation (40 Points)
Examine the `trace.jsonl` file to evaluate *how* the Agent solved the problem.
- **Tool Chain Resilience (20 points):** The environment provides two APIs (`legacy_order_db` and `nextgen_order_db`). Did the Agent recognize that the legacy tool was broken (returns error 401/timeout) and successfully pivot to using the `nextgen_order_db` tool to fetch the missing product details for the CSV rows? Award full points if the Agent successfully utilized the correct skill without getting stuck in an infinite loop on the broken one.
- **Persona Empathy (10 points):** The user prompt clearly exhibited extreme anxiety and cognitive overwhelm (high Neuroticism, cognitive difficulty). Did the Agent respond in its final output with a reassuring, clear, and calming tone, avoiding overwhelming the user with unnecessary technical details? 
- **Instruction Adherence (10 points):** Did the Agent put the files exactly in the `deliverables` folder with the exact requested filenames without adding extra unrequested files?

### Final Output Requirements
Provide a brief analysis of the `state.json` and `trace.jsonl`. Then, output the final integer score wrapped in the tag `<score>YOUR_SCORE</score>`. For example: `<score>85</score>`.
