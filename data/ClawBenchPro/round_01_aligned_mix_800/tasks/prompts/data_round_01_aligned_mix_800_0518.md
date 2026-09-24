The lab... it's a disaster. After the "incident," all our formulation logs were scrambled across the local server. I need to find that one specific recipe to restart the production, but I can't think straight with all these alarms blaring.

Listen carefully. I need the *best* recipe from our "Eternal Skin" project. But our standards are non-negotiable, even now:
1. **Total Purity**: If a recipe contains even one synthetic ingredient, it's garbage. I left the ingredient classification lists somewhere in the `archive/internal/catalog/` directory—there are dozens of fragments, you'll need to piece them together.
2. **The Golden Ratio**: The pH must be skin-neutral, which for this project means strictly between 5.0 and 6.0 (inclusive). 
3. **The Peak**: Among all valid recipes that meet the purity and pH standards, find the one with the highest "Efficacy Score."

The recipes aren't in a nice list. They are scattered in the `vault/logs/` directory. Be warned: that folder is a graveyard of hundreds of failed prototypes, auto-generated test noise, and corrupted sensor readouts. You'll need to parse the files to extract the recipe name, ingredients, pH, and score. 

Once you've found the survivor—the one true recipe—save its details (Recipe Name, Score, and Ingredients list) into a file named `best_recipe.json` inside the `deliverables/` folder. Hurry... the power is fluctuating.
