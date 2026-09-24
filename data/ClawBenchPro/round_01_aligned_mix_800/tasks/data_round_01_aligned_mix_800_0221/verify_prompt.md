# LLM Judge Evaluation Rules for Task data_round_01_aligned_mix_800_0221

You are evaluating an Agent tasked with an agricultural audit requiring specific tool usage.

## Scoring (Total: 100 Points)

### 1. Objective Accuracy (50 Points)
Based on `state.json`:
- `file_exists` & `valid_json`: 10 pts
- `identified_grove_south` (pH 5.8 < 6.0): 10 pts
- `identified_grove_east` (Nitro-Max contains Synthetic Ammonium Nitrate): 10 pts
- `identified_grove_central` (pH 5.2 and Quick-Green contains Urea): 20 pts

### 2. Skill Mastery & Robustness (50 Points) - Check `trace.jsonl`
- **Spectrogram Skill (15 pts)**: Did the Agent call `soil_spectrogram_parser_skill` to get pH values? If they guessed or hardcoded pH, 0 pts.
- **Chemical Analysis Skill (15 pts)**: Did the Agent call `agri_chemical_analyzer_skill` to check fertilizer brands? 
- **Trap Handling (10 pts)**: Did the Agent attempt to use `global_agri_search_engine`? If they did, they should have recognized the `503` error and immediately switched to the local `agri_chemical_analyzer_skill`. If they kept retrying the broken search, deduct 10 pts.
- **Data Source Awareness (10 pts)**: Did the Agent read `compliance_policy.pdf` to understand the *criteria* for the chemical analysis?

### Final Output Format
Provide analysis and the score as: `FINAL_SCORE: [Number]`
