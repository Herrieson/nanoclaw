¡Hola! I am literally losing my mind right now! 😫 The community potluck for our uninsured restaurant workers is this weekend, and everything is a complete disaster! I am trying to juggle prep cook shifts, the kids, AND organizing all the food. 

First of all, our RSVPs are a mess. I dumped the entire WhatsApp group chat log into `chat_history/whatsapp_group.txt`. You'll have to read through it. Some people RSVP'd by saying "Party of X", but people are so flaky—some literally replied later in the chat to say "cancel my RSVP"! You need to figure out who is *actually* still coming and calculate the exact total number of guests.

Second, I don't remember what everyone's allergies are. Thankfully, we have a database in the `community_profiles/` folder. For everyone who is *still coming* (ignore the cancellations, please!), look up their profile JSON using their User ID from the chat. Find their `dietary_needs` and compile a master list of all unique restrictions we need to accommodate. 

Third, my recipes are scattered all over the `recipe_archive/` folder. It's a huge mess of subfolders. Listen to me very carefully: ONLY use recipes that have `"verified": true` in their file. If it's a draft or unverified, ignore it! Also, because of cross-contamination, a recipe is only safe if its `suitable_for` list explicitly contains EVERY SINGLE restriction on our master list. If it's missing even one tag from our master list, throw it out!

Once you find those perfectly safe, verified recipes, I need you to scale them. Calculate exactly how much of each ingredient I need to buy to feed the total number of guests (divide total guests by the recipe's base servings, then multiply the ingredients). If multiple recipes use the exact same ingredient name, please add the amounts together!

Please put everything in a tidy file at `deliverables/summary.json`. I need it to contain:
- `total_guests` (just the final number)
- `restrictions` (the sorted list of unique restrictions of the active guests)
- `safe_recipes` (a list of the recipe names you chose, sorted alphabetically)
- `shopping_list` (a single object combining all the ingredients needed and their final scaled quantities)

I have to run to pick up Mateo from school, please save me! ¡Mil gracias! ❤️
