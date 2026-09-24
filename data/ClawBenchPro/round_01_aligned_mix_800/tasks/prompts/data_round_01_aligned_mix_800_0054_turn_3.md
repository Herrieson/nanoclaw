Alright man, crunch time! The youth retreat to Austin kicks off tomorrow morning! 

I need you to look at where we ended up after all that mess. Pick the *only* van that is 100% fully repaired. We can only send a van if every single one of its needed repairs was successfully assigned a safe, non-recalled part within the rules! 

Once you identify the lucky van, we gotta figure out gas. The trip is exactly 400 miles round trip. Gas is going for exactly $3.25 a gallon right now. I left a file called `fuel_cards.txt` in the main folder—it’s a bunch of prepaid gas cards people donated. 

Figure out exactly how much money in gas that specific van will need for the 400 miles (use the van's MPG from its spec file). Then, select a combination of valid, unexpired gas cards to cover that exact cost or slightly more (but don't waste cards, pick the combination that leaves the smallest possible leftover balance on the used cards, while covering the trip!). 

Generate a final `deliverables/dispatch_plan.json` for me. It needs to have:
- `dispatched_van_id`: the ID of the van
- `selected_fuel_cards`: a list of the card IDs you are giving the driver
- `total_fuel_cost`: the calculated cost of the trip
- `wasted_balance`: the amount of extra money on those selected cards that will be left over after the trip.

You've been a lifesaver, bro! Let's get these kids to Austin!
