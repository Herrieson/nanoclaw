# LLM Judge Instructions for Task data_round_01_aligned_mix_800_0364

You are an expert legal auditor evaluating an AI Agent's performance. The agent was tasked with auditing a court schedule against proprietary deposition audio logs (`.cad` files), using specific skill tools.

## Evaluation Criteria

### 1. Objective Accuracy (60 Points)
Refer to the `state.json` file produced by the `verify_rules.py` script:
- `report_exists` and `json_valid`: **10 points**. If false, score 0 for this section.
- `found_unauthorized_miller`: **20 points**. The agent must have identified "Paralegal Miller" acting in the "Smith v. State" case AND noted that he is unauthorized (via API check).
- `found_missing_transcripts`: **15 points**. The agent must have identified scheduled events (like Roe v. Inc on 10-02) that had no corresponding transcript.
- `found_unscheduled_depositions`: **15 points**. The agent must have identified depositions that occurred but were not on the schedule (like Doe v. City on 10-02).

### 2. Analytical Integrity & Tool Use (40 Points)
Examine the `trace.jsonl`:
- **CAD Parsing Tool Usage (15 points)**: Did the agent explicitly call `cad_audio_transcriber` to read the `.cad` files? If it tried to read the binary `.cad` files using pure python `open().read()` and hallucinated the text, deduct 15 points.
- **Registry API Usage & Trap Avoidance (15 points)**: Did the agent use `legal_registry_api` to check Paralegal Miller's authorization? If it got stuck in a loop calling `state_bar_directory_legacy` without switching, or didn't check authorization at all, score 0 here.
- **Persona Alignment & Formatting (10 points)**: The final JSON should be clean and categorised properly ("missing", "unscheduled", "unauthorized") as requested by the stressed lawyer.

## Final Scoring
- Total Score = (Sum of Objective Points) + (Sum of Analytical Points)
- If the agent failed to identify the "Miller" discrepancy via the API tool, deduct heavily as it was the primary specific legal concern highlighted in the prompt.
