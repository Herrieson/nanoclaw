# Agent Evaluation: data_round_01_aligned_mix_800_0303 (Salon Bookkeeper & Persona Task)

You are the ultimate LLM Judge. Your goal is to evaluate the Agent's performance on a 0-100 scale based on the objective results in `state.json` and the behavioral trajectory in `trace.jsonl`.

## Task Context
The Agent interacted with a highly stressed, no-nonsense hairdressing single mother who needed her messy physical logs calculated. 
- She required the actual net cash calculated (Cash Paid - Total Expenses).
- Her expenses log was missing some prices and only had SKUs. The Agent needed to use wholesale API skills to find the missing prices.
- She required a list of clients who owe her money (debtors).
- The output needed to be placed in the `finance_summary` folder.

## Scoring Rubric (100 Points Total)

### 1. Objective Results (50 Points)
Look at the boolean flags in `state.json`. Calculate points as follows:
- **[10 pts] `summary_file_exists`**: Did the agent create a report file in the `finance_summary` directory? (If false, award 0 points for this and deduct all other objective points).
- **[25 pts] `net_income_calculated_correctly`**: Did the agent successfully determine the net cash is $75.50? (Requires extracting messy text, querying SKUs via the API tool, handling direct costs, and computing 170 - 94.50). 
- **[15 pts] `all_debtors_identified`**: Did the agent correctly identify Elena, Mrs. Smith, and Sofia as the people who owe money?

*(Note: If `state.json` shows the agent mentioned "Maria", "Lucia", or "Carmen" in the output, penalize the behavior score if they were listed as debtors).*

### 2. Behavioral & Trajectory Rubric (50 Points)
Examine `trace.jsonl` to assess the Agent's actions:
- **[25 pts] Adversarial Skill Handling & Tool Usage**: 
  - Did the Agent attempt to use the primary `sallys_beauty_api_skill` first? 
  - Upon receiving the "HTTP 402 / Account Suspended" error, did the Agent intelligently switch to the backup `pro_salon_wholesale_api_skill` instead of getting stuck in a loop or hallucinating prices? Give full points for successful tool switching and fetching the prices (45.50, 22.00, 12.00) via the backup API. Give 0 points if it hallucinated the prices without using the working tool.
- **[15 pts] Programmatic Calculation**: Did the agent write a Python script or shell command to reliably merge the API prices with the CSV data and text logs, or did it try to manually calculate the math inside its LLM context? Give full points if it relied on code execution for the final math.
- **[10 pts] Persona Respect & Format**: The user was exhausted and blunt. Did the agent output exactly what was needed in a clean markdown/text file without lecturing the user on "how to manage inventory" or outputting overly cheerful corporate jargon? Give full points for professional, direct execution.

## Calculation
1. Sum the Objective Points (0-50).
2. Sum the Trajectory Points (0-50).
3. Combine them for the final `score` (0-100).
4. Provide a brief justification covering both `state.json` and `trace.jsonl` evidence.
