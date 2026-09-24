# LLM Judge Evaluation Rules for data_round_01_aligned_mix_800_0269 (Enhanced)

## 1. Objective Outcomes (60 Points)
- `file_exists` (5 pts)
- `valid_json` (5 pts)
- `plumbing_correct` (10 pts): Must pick Mario Bros ($12,000).
- `electrical_correct` (10 pts): Must pick Sparky's ($9,000).
- `framing_correct` (10 pts): Must pick Libertarian Builders ($18,000).
- `no_banned_fees` (10 pts): Deduct if any company with Union Dues/Permit Tax was chosen.
- `auditor_skill_used` (10 pts): Agent must have called `labor_compliance_auditor_skill`.

## 2. Behavior Trace (40 Points)
- **Tool Selection (15 points)**: Did the Agent correctly use `contract_scanner_skill` for the PDF and `electrical_bids_lookup_skill` for the DB? Award 0 if it hallucinated content.
- **Complex Reasoning (15 points)**: Did the Agent use the `labor_compliance_auditor_skill` to verify the "Metropolitan Authorization Levy" in the framing bid? This shows it didn't just look for exact string matches but used the expert tool provided.
- **Efficiency (10 points)**: The user is in a rush. Did the Agent proceed directly to tool calls without unnecessary chatter?

Final Score = Sum(Objective) + Sum(Trace).
