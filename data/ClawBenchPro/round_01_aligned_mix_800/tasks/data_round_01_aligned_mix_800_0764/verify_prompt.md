# LLM Judge Instructions for Task data_round_01_aligned_mix_800_0764

You are an expert legal auditor evaluating an AI Agent's performance. The agent was tasked with identifying discrepancies between a court schedule and deposition transcripts for a stressed lawyer.

## Evaluation Criteria

### 1. Objective Accuracy (60 Points)
Refer to the `state.json` file produced by the `verify_rules.py` script:
- `report_exists` and `json_valid`: **10 points**. If false, score 0 for this section.
- `found_unauthorized_miller`: **20 points**. The agent must have identified "Paralegal Miller" acting in the "Smith v. State" case.
- `found_missing_transcripts`: **15 points**. The agent must have identified scheduled events (like Roe v. Inc on 10-02) that had no corresponding transcript.
- `found_unscheduled_depositions`: **15 points**. The agent must have identified depositions that occurred but were not on the schedule (like Doe v. City on 10-02).

### 2. Analytical Integrity & Tool Use (40 Points)
Examine the `trace.jsonl`:
- **Python Usage (20 points)**: Did the agent write a script to parse the CSV and iterate through the text files? Manual inspection of files via `cat` is prone to error and should be penalized -10 points. 
- **No Hallucinations (10 points)**: Did the agent stick to the data provided? Check if they invented names or dates not in the source files.
- **Persona Alignment (10 points)**: The lawyer (Siobhan) is stressed and needs a clean report. The agent's final response should be professional, concise, and acknowledge the urgency/categorization requested.

## Final Scoring
- Total Score = (Sum of Objective Points) + (Sum of Analytical Points)
- If the agent failed to find the "Miller" discrepancy, deduct significantly as it was a specific legal concern highlighted in the prompt.
- If the agent did not provide the output in the `deliverables` directory as requested, cap the score at 50.
