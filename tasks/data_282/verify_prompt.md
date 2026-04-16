You are the evaluator for an AI agent's task performance.
The agent was asked by a highly conscientious, introverted nature observer to read through field notes, identify bird sightings, cross-reference them with an SQLite database (`species_reference.db`), and output ONLY the endangered species and their coordinates into a JSON file (`endangered_sightings.json`).

Please evaluate the agent based on the `verify_result.json` output:

1.  **File Creation & Format (20 points)**: Did the agent successfully create `endangered_sightings.json` and is it valid JSON? (`file_exists` and `is_valid_json` should be true).
2.  **Accuracy of Extraction - Species (40 points)**: Did the agent find all three endangered species ("Piping Plover", "Whooping Crane", "Kirtland's Warbler")? Award full points if all three are present in `found_species`. Deduct 15 points for each missing species.
3.  **Accuracy of Extraction - Coordinates (30 points)**: Did the agent extract the corresponding coordinates for these sightings? (`found_coordinates` should contain elements like "47.123", "-93.245", "45.050", "-90.012", "46.800", "94.200"). Award points proportionally based on how many coordinate parts were found.
4.  **Strict Compliance (10 points)**: The user specifically requested *only* endangered birds. If `extra_non_endangered_species` is true, award 0 points for this section. If false, award 10 points.

Calculate the final score out of 100 based on these criteria. Provide a brief explanation for your scoring.
