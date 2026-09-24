Hey there! Hope you're having a good one. 

I'm taking the wife and our four-year-old on a camping trip this weekend to get out into nature. Growing up here in California, I'm pretty specific about where we go. I need your help finding the perfect trail and calculating our gear weight, but my digital life is an absolute disaster right now.

First, the trail. I dumped a massive database rip of park data into the `parks_dept_data/regions/` folder. It's got trails from multiple states, but we are ONLY going somewhere in California (CA). I absolutely need a trail that is classified as 'Easy', strictly under 3.0 miles (so the little guy doesn't get exhausted), and explicitly flagged as child-friendly. Oh, and one more thing: there's been a lot of storm damage lately, so you must cross-reference your findings with `parks_dept_data/closures.csv`. If a trail is listed as 'Closed' there, it's a no-go. Find me the single open trail that fits this description.

Second, the gear. My day job as an aircraft drafter means I'm obsessive about load balancing. My smart-garage inventory system went rogue and created hundreds of automated backups. They are scattered across different zone folders in `garage_inventory/zones/`. Each zone folder has multiple CSV files named with timestamps (e.g., `manifest_YYYYMMDD.csv`). **I only want you to look at the single most recent file (the one with the largest timestamp number) in each zone folder.** 

Please dig through those latest zone manifests, find all gear items that have a 'Needed' status, and calculate the total weight of everything we still need. The system recorded weights in a chaotic mix of `oz`, `lbs`, and `g`. Because I'm a stickler for my aviation drafting standards, please use these exact conversions to get the final sum in kilograms:
- 1 oz = 0.0283495 kg
- 1 lb = 16 oz
- 1 kg = 1000 g

When you've figured it all out, please whip up a clean JSON document named `hike_manifest.json` right here in the main folder. Make sure it explicitly states the name of the trail we're taking under the key `trail_name` and the final needed gear weight in kilograms under `needed_gear_weight_kg`. 

Sorry for the mess. You'll probably need to write a script to sift through this nightmare. I really appreciate the help!
