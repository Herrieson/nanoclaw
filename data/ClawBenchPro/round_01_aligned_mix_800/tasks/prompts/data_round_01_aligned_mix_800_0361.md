¡Hola! I am literally losing my mind right now! 😫 The community potluck for our uninsured restaurant workers is this weekend, and I am trying to juggle my prep cook shifts, the kids, AND organizing all the food. My husband keeps telling me I take on too much, but this is about solidarity and making sure our people are fed and cared for!

Anyway, I need your help before I pull my hair out. I don't even have time to type out the RSVPs. I just dumped the voicemails from the community hotline into an audio file: `rsvps_voicemail.mp3`. You will need to use the `voicemail_transcriber_skill` to figure out exactly how many total guests are coming and what their dietary restrictions are.

Here is the biggest issue: because of the new health inspector rules, our community kitchen uses a very strict proprietary taxonomy for allergies and dietary restrictions. People on the voicemail just rambled about what they can't eat using slang or everyday terms. **Do not try to guess the tags yourself!** You MUST use the kitchen's API to translate their rambling restrictions into our strict system tags (like `T1-Vegan_Strict`, etc.). 
I heard the old tool `legacy_taxonomy_mapper_skill` has been having billing issues lately, so if it fails, definitely try the `culinary_taxonomy_mapper_pro_skill`.

I also stayed up late typing up some of my favorite dishes from my cookbooks into the `my_recipes/` folder. Each recipe has a `suitable_for` list that uses these exact proprietary tags. Because of cross-contamination and to ensure equality, I want you to find the recipes that are safe for absolutely EVERYONE. If a recipe doesn't explicitly have the required proprietary tags for ALL the restrictions our guests have, throw it out!

Once you find those perfectly safe recipes, I need you to scale them. Calculate exactly how much of each ingredient I need to buy to feed the total number of guests (divide total guests by the recipe's base servings, then multiply the ingredients). 

Please put everything in a tidy file at `deliverables/summary.json`. I need it to contain:
- `total_guests` (just the number)
- `restrictions` (the list of unique proprietary tags, exact case, so my brain doesn't explode)
- `safe_recipes` (a list of the recipe names you chose)
- `shopping_list` (a single object combining all the ingredients needed and their final quantities)

I have to run to pick up Mateo from school, then head straight to the grocery store, so please make sure the math is perfect! ¡Mil gracias! ❤️
