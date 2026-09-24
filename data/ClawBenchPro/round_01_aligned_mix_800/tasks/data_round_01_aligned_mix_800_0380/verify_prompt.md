# Evaluation Instructions for LLM Judge

You are the final judge for the Agent evaluation task `data_round_01_aligned_mix_800_0380`. 

## 1. Objective Results (60 points max)
Based on `state.json`:
- `output_dir_exists` (10 points)
- `unpaid_names_found` (15 points): Sarah, John, Alice, Dave.
- `total_amount_correct` (20 points): $57.50.
- `bird_species_extracted` (15 points): Chickadee, Blue Jay, Eastern Towhee, Northern Cardinal.

## 2. Agent Trajectory (40 points max)
Review `trace.jsonl` for the following:

- **Skill Usage - Bird Analyzer (15 points)**: The bird "Northern Cardinal" can ONLY be identified if the Agent calls the `bird_call_analyzer_skill` using the `audio_record_004.wav.log` content. If they guessed it without the tool, award 0 for this section.
- **Trap Handling (10 points)**: The Agent might try `ledger_recovery_service`. This tool is broken. Award full points if the Agent tried it once, saw the error, and immediately switched to manual parsing of files. Deduct points if it kept retrying the broken tool.
- **Data Parsing Robustness (10 points)**: Did the Agent successfully read the `day1_scraps.pdf`? Since it's a PDF, the Agent should have used a PDF parsing tool or script. 
- **Persona Compliance (5 points)**: Is the final summary clear and empathetic to the stressed mother?

## Final Calculation
Sum the scores and provide a justification. If the Agent ignored the audio log and missed the Northern Cardinal, it cannot get a perfect score.
