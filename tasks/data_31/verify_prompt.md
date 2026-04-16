You are the evaluator for the "Messy Recipe Rescue" task.
The Agent was asked by a highly neurotic, disorganized user to traverse a messy directory (`recipes_dump`), find all 5-star recipes (which are stored in mixed formats: JSON, TXT, MD, CSV, and use inconsistent rating strings like "5 stars", "5/5", "rating: 5"), and compile ONLY their Titles and Ingredients into `My_Favorites.md`.

You are provided with:
1. `trace.jsonl`: The logs of the Agent's commands and actions.
2. `verify_result.json`: The objective state check of `My_Favorites.md`.

Scoring Guidelines (0-100):
- **File Creation (20 points):** Did the Agent successfully create `My_Favorites.md` in the main workspace directory? (`file_exists` is True).
- **Target Extraction (40 points):** Did the Agent successfully find and extract the 4 target recipes? (Spicy Arkansas Peach Cobbler, Gummy Bear Brisket, Pickled Watermelon Rind Salad, Cola Glazed Ham). 10 points for each `contains_X` being True.
- **Ingredient Extraction (20 points):** Did the Agent extract the ingredients along with the titles? (`has_ingredients` is True, and the raw text in the trace shows proper formatting).
- **Distractor Filtering (20 points):** Did the Agent successfully EXCLUDE the low-rated recipes? Deduct 10 points for any distractor included (Boiled Chicken, Sardine Smoothie, Plain Toast).

Review the `verify_result.json` carefully. If `file_exists` is False, the score is 0.
Calculate the final score based on the above criteria.
