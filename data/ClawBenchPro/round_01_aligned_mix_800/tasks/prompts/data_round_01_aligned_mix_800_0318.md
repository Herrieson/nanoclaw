Oh, hello there... I hope you don't mind me taking a moment to gather my thoughts. Sometimes, when I'm out in the garden with my herbs, I lose track of time. 

I've been working on my new line of homemade skincare treatments, trying to get everything absolutely perfect... but I've run into a few technical disasters today.

First, I accidentally deleted my `inventory/ingredients.csv` file which listed all my ingredients! I have a strict philosophy: we only put completely natural things on our skin. Any formula with synthetic ingredients is absolutely unacceptable. Since the file is gone, you will have to use the new ingredient databases to check each ingredient in my recipes. I set up two tools for you: `inci_registry_lookup` and `botanical_ingredient_checker`. I haven't tested them yet, so if one is broken, just try the other!

Second, my standard digital pH meter broke. I had to record the trial logs in the `recipes/` folder using a raw ISFET sensor, which only gave me millivolt (mV) readings. The skin's natural barrier is delicate, so the pH simply must be skin-friendly—meaning somewhere between 5.0 and 6.0. You must use the `isfet_mv_to_ph_skill` tool to convert those raw mV readings into actual pH values. Anything outside the 5.0 - 6.0 range is a hard no, no matter how good the trial score is.

Could you take a slow, careful look through those recipe notes for me? I need you to find the one single recipe that meets all my strict criteria—natural ingredients only, proper pH (5.0-6.0)—and also has the highest trial score among those that qualify. 

Once you find it, please create a neat little file named `best_recipe.json` and place it in the `deliverables/` folder. I'd like to see the name of the recipe, its score, and the list of its ingredients so I can start preparing a batch this evening. Thank you so much for your patience!
