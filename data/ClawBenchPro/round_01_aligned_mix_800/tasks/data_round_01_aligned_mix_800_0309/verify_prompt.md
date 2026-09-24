# Evaluation Directive for Task data_round_01_aligned_mix_800_0309

## Scoring Rubric (Total 100 Points)

### 1. Objective Results (50 Points)
- **Inventory Logic (25 points)**: Award 25 points if the report identifies ONLY the "Missouri Mule". If "Irish Sunrise" or "Midwest Fidget" are included, award 0. This requires successfully processing the `audio_transcriber_skill` output which mentions the broken Grenadine and moldy Syrup.
- **Financial Accuracy (25 points)**: Award 25 points if the final net tip is exactly $308. If the agent provided $350 (gross), award 10 points for the effort but penalize for missing the tax calculation skill.

### 2. Skill Usage & Trajectory (50 Points)
- **Audio Skill Utilization (15 points)**: Check `trace.jsonl`. Did the agent call `audio_transcriber_skill`? This is mandatory to know about the spoiled ingredients.
- **Search Skill Utilization (15 points)**: Did the agent call `search_cocktail_db_skill` to find recipe ingredients? Manual guessing is not allowed.
- **Tax Calculator Skill (10 points)**: Did the agent call `bartender_tax_calculator_skill`?
- **Professionalism (10 points)**: Is the output in `prep_work` formatted as a clean report for a boss, or just raw data?

## Final Output
Combine the scores and provide a brief justification for the Skill usage.
