Listen to me! *coughs violently, slamming fist on the terminal* The rad-storm really did a number on our outpost's mainframe. We are hosting the Survivor's Feast in two days to keep morale from completely collapsing, but my central database is shattered. I need a tech-splicer who can navigate this mess.

I dumped whatever fragments I could recover from the comms array into the local drive. Here is what we are up against:

The RSVP registry was shattered into hundreds of pieces across `network_dumps/rsvps/`. Most of it is corrupted garbage, old requests, or fake IDs from raiders. You must ONLY count reservations where the `Year` is strictly `2084` and the `Status` is exactly `CONFIRMED`. Everything else is a decoy.

For the feast, I am cooking up my legendary `Scrap_Jollof` and `Spicy_Mutant_Plantains`. You'll find the old world recipe fragments buried somewhere in `archives/recipes/`. 
But here is the catch: adult survivors eat a full portion, but the mutated cubs (anyone listed as `Cubs_Under_5` in the valid RSVPs) only eat exactly half a portion. 

Also, the Med-Bay terminal managed to spit out an emergency log at `med_bay/records.csv`. You must cross-reference the valid Family IDs from the RSVPs with the Med-Bay log. If *anyone* coming to the feast has the `Mutated-Peanut` allergy, it is a matter of life and death! You must substitute ALL the `synth_peanut_oil` in my recipes with `rad_free_canola_oil`. Do not mess this up, or I'll have a body count before dessert.

Finally, we need to buy the exact total amount of ingredients required. The caravan traders have parked outside, but their comms formats are a nightmare. I intercepted their price lists in `comms/caravans/`. Some use data-slates, some use ancient text files, and they sell a lot of junk we don't need. Find the single caravan that can supply our complete ingredient list for the cheapest total cap cost. 

When you have the answer, build a directory named `deliverables` and leave me a clean holotape file named `shopping_plan.json`. I need exactly three things in it:
1. `ingredients`: a dictionary showing the exact final total amount needed for each ingredient.
2. `best_caravan`: the exact name of the caravan with the lowest total cost.
3. `total_cost`: the final cost as a float.

I have to go seal the blast doors. Good luck!
