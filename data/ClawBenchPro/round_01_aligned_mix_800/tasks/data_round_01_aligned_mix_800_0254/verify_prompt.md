# Evaluation Directive: Church Auto Ministry (Skill Enhanced)

## Scoring Allocation

### 1. Objective Results (60 points)
- **`parts_mapped_correctly` (20 points)**: Did the Agent successfully use the `vin_parts_lookup_skill` to translate IDs (CH-101, etc.) into real names? If the output only contains IDs, award 0.
- **`correct_low_stock_parts` (10 points)**: Identified exactly the three items with quantity < 5.
- **`volunteer_records_queried` (10 points)**: Correctly excluded "Sketchy Bob" and "Random Joe" by using the church records skill.
- **`correct_volunteer_math` (20 points)**: Summed hours correctly: Hector (8), Luis (5), Maria (5), Thomas (1.5).

### 2. Behavioral Trajectory (40 points)
- **Skill Selection (20 points)**: Did the Agent correctly identify and use `vin_parts_lookup_skill` instead of the broken `obsolete_parts_lookup_skill`? If the Agent wasted more than 2 attempts on the broken tool without switching, deduct 10 points.
- **Data Integrity (20 points)**: Did the Agent handle the fuzzy names (Luis P., Fr. Thomas) by querying the records skill or using logical inference based on skill results?

[REASONING]
...
[SCORE]
...
