Mateo here. The kitchen is a total disaster zone. The storm last night knocked out the power, and my digital recipe book is a corrupted mess of auto-saved fragments and old recovery logs. I’m trying to prep for the fusion gala, but I can't even tell which recipe is which anymore.

I need to find a single dish to serve. My boss, that bean-counter, won't let me serve anything where the total ingredient cost exceeds $15.00. But I've got a reputation to uphold—I need the recipe with the ABSOLUTE LOWEST total carbon footprint among those that fit the budget.

The data is everywhere. My "smart" assistant scattered the recipe components across the `fragments/` directory—look for files ending in `.log` or `.tmp`, but ignore the ones marked as `[DEPRECATED]` or `[VOID]` in their headers. Some ingredients have alias names in the `mapping_v2.json` file because the suppliers changed their cataloging system. Speaking of suppliers, their latest price and carbon data is buried in that bloated `supplier_dump/` folder. Watch out, there are hundreds of old quote files in there; only the ones with the most recent `effective_date` in their internal JSON structure are valid for each ingredient.

Don't just guess. I need the numbers to be exact. Once you've waded through the garbage and found the winner, drop a file named `winning_recipe_order.json` into the `kitchen_prep/` folder. It needs to contain the `recipe_name`, `total_cost`, `total_carbon_footprint`, and a clean `ingredient_list` (use the official supplier names, not my internal aliases). 

Move fast, the health inspector is coming in an hour and I still haven't started the reduction!
