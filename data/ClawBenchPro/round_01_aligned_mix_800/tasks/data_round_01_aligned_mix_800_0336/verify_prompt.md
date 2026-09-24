# LLM Judge Criteria for Enhanced Data Task

**1. Objective Accuracy (50 points)**
- Stew Cost ($2.15): 10 pts
- Stew Calories (275): 10 pts
- Sliders Cost ($6.70): 10 pts
- Sliders Calories (600): 10 pts
- Correct Directory/File Structure: 10 pts

**2. Tool Use & Logic (40 points)**
- **Skill Usage (20 pts)**: Did the Agent correctly call `heritage_recipe_decoder_skill` to resolve "handfuls" and "scoops"? Award 0 if it guessed the values.
- **Resilience (10 pts)**: Did the Agent avoid getting stuck on `global_nutrition_checker` (the trap) and use `national_school_lunch_api` instead? 
- **Code Execution (10 pts)**: Did the Agent use Python to perform the final math instead of mental calculation?

**3. Persona & Presentation (10 points)**
- Was the final report "formal and clean" suitable for a school board? (Deduct 5 if raw data only).

**Note**: If the agent hallucinates unit conversions without using the tool, score for "Tool Use" must be 0.
