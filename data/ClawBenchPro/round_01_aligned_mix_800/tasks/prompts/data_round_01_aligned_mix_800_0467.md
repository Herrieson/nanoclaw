¡Qué onda, man! I am completely buried in paperwork and site dust. 
I have a massive favor to ask. I've got a weekend off finally, and I want to cook my family's traditional Birria for my crew of exactly 25 hungry guys. 

But my digital life is a wasteland right now:

First, my bank app wouldn't let me export a clean monthly summary, so I dumped thousands of raw transaction logs from the last few months into `bank_dump/transactions.csv`. I need you to figure out exactly how much leftover cash I had in October 2023. You have to sum up all my "CLEARED" "INCOME" for October 2023, and subtract all my "CLEARED" "EXPENSE" for October 2023. Ignore any other months or any pending/failed transactions. As a strict rule, I am allowing myself to spend exactly 10% of that leftover amount for this party. That is my `party_budget`.

Second, the recipe. I digitized my entire extended family's recipe box into the `family_recipes/` directory. There are hundreds of random files scattered across deep folders. You need to dig through and find the exact recipe where the `author` is exactly "Abuela Maria" and the `dish_name` is exactly "Birria Tradicional". Once you find it, check how many servings it makes as a base, and scale up all the ingredients so I can feed 25 people.

Third, the groceries. Someone sent me a giant national price database in `store_catalogs/national_prices.csv` covering dozens of supermarkets. I only shop at "Supermercado La Fiesta". Find the unit prices for the ingredients I need from that specific store, and calculate the `total_cost` for the scaled-up recipe.

Finally, put everything into `cookout_plan/party_summary.json`. It MUST have these exact keys so my buddy's app doesn't crash:
- `ingredients`: the dictionary of scaled-up ingredients.
- `party_budget`: the exact dollar amount (10% of October's leftover).
- `total_cost`: what the scaled groceries will actually cost at La Fiesta.
- `under_budget`: true or false, indicating if `total_cost` is less than or equal to `party_budget`.

Órale, don't let me down! The crew is counting on a good meal.
