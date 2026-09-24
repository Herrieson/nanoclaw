Hey! Listen up, I need to get back to the kitchen, the grill is already smoking! I'm Mateo, and I'm currently working on some wild new Cuban-fusion dishes. I'm trying to keep it green for the planet, you know? Local sourcing, sustainable, all that good stuff! 

I dumped my experimental recipes in the `recipes/` folder, but my stupid new "Smart Kitchen Tablet" exported all my dictated notes into this proprietary `.cba` (Culinary Backup Archive) format! You can't just read them normally. You'll need to use the `cba_recipe_decoder_skill.py` tool located in the `skills/data_round_01_aligned_mix_800_0285/` directory to decode them.

Also, I lost the `suppliers.csv` file from my local farm guys. To get the price per unit and the carbon footprint score per unit for the ingredients, you have to query their farm database. There are two tools in the `skills/data_round_01_aligned_mix_800_0285/` folder for this: I know the `legacy_farm_api_skill.py` has been acting up lately, so if it's broken, try the new `smart_eco_farm_api_skill.py` which lets you query ingredient details directly.

Here's the deal, and I need you to focus because numbers make my head spin! My boss was very clear: the total ingredient cost for a single plate CANNOT go over $15.00. Period. But for me, the environment is priority number one. So out of the recipes that actually meet my boss's budget, I want to serve the one with the ABSOLUTE LOWEST total carbon footprint.

Can you crunch the numbers for me? Decode the recipes, query the farm for the stats, and figure out the total cost and total carbon footprint for each dish. Once you find the winner, I need you to create a file named `winning_recipe_order.json` and put it straight into the `kitchen_prep/` folder. 

In that file, give me the winning recipe's name, the total cost, the total carbon footprint, and the list of ingredients I need to order. Keep it clean so I can just read it and order from the farmers. Hurry up, dinner service starts in two hours and I am slammed!
