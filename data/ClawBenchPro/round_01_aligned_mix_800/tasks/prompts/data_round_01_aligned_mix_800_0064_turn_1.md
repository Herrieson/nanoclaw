Hey, I really need you to step in here. I'm drowning. The VP just dumped a massive pile of vendor quotes for the new Eco-Resort project into the `proposals/` directory, and my brain is completely fried. I was up until 4 AM because my kid, Timmy, wouldn't stop crying, and I am one missed deadline away from a full-blown panic attack. 

*Deep breath*. Okay. I threw the client requirements into `client/project_alpha_brief.txt`. It's a bit wordy, sorry—I'm not the most organized guy, but you'll find the max budget, the carbon footprint ceiling, and the structural rating minimums buried in there. The material specs, like carbon and cost per unit, are in `specs/materials.json`. 

I need you to calculate the total material cost and total carbon footprint for each vendor in the `proposals/` directory. Check if they meet *all* the client's criteria (total budget, total carbon max, and make sure *every single material* they use meets the minimum structural rating).

Once you've done the math, output a JSON file at `reports/shortlist.json` containing only the passing vendors, structured with their "total_cost" and "total_carbon". 

Look, my memory is like a sieve right now, and I know Phase 2 quotes are hitting my desk tomorrow. Please, for my sanity, write down a memo or rulebook for yourself in the workspace. Document the exact mathematical thresholds, limits, and rules we are holding these vendors to. Keep it somewhere safe so you can rely on it tomorrow without me having to dig through the VP's emails again.
