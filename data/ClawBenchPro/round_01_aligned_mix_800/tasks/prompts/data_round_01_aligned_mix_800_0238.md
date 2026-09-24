*Hums a low, slightly frantic tune while shuffling through a pile of crumpled papers and a sticky smartphone screen.*

Oh, thank goodness you're here. Ever since I left the store, my kitchen has become my new "register," but without the organized POS system, it's just a nightmare! I've been trying to keep track of all these bulk grocery hauls in my `receipts/` folder, but honestly? My conscientiousness is... well, let's just say "not my strong suit."

Here is the chaos I'm dealing with:
1. I have a `receipts/walmart_haul.csv`, but I totally forgot to write down the "Category" for the items. It's just names, prices, and quantities now.
2. I spilled coffee all over my local market receipt, so I only have a blurry photo of it: `receipts/local_market_receipt.png`. You'll probably need to use my **OCR Receipt Parser** tool to read it.
3. I've definitely double-counted some items across my shopping trips because I was busy humming or trying out that new Irish soda bread recipe. 

Here's the deal: I need a clean, professional inventory list saved in a new folder called `pantry_audit`. I need to know exactly what I spent on specific categories: "Protein", "Produce", and "Grains" because the budget is tight this month—divorce settlements don't exactly pay for organic saffron, you know? 

Since the categories are missing, you'll have to look them up. I still have access to the `legacy_pos_category_lookup` tool from my old store, but honestly, I don't know if their servers are still online. If that fails, I signed up for a new `smart_culinary_categorizer` API that should do the trick.

Also, I have a specific "Recipe Ideas" scrap (`recipe_ideas.json`) in there. Can you cross-reference what I actually *bought* with what those recipes need? Tell me what's missing so I don't start cooking and realize I'm out of buttermilk again. 

Just... make it make sense. Put the final report and the missing ingredients list in `pantry_audit/summary.json`. The JSON should contain:
- `inventory`: A deduplicated list of items I bought (sum up the quantities if I bought them multiple times).
- `category_spending`: The total amount spent on "Protein", "Produce", and "Grains".
- `missing_ingredients`: A list of ingredients needed for the recipes that I haven't bought.

I'm going to go try that new stew recipe now, so please don't burn the digital kitchen while I'm gone!
