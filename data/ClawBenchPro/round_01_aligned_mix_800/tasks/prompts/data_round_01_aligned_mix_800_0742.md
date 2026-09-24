Listen, I have exactly ten minutes before I have to leave to pick up my toddler from daycare, and I do not have the patience for incompetence today. I'm running on fumes, and I just walked in to find that the weekend pharmacy temps left our inventory logs an absolute disaster. It's completely disorganized, and cleanliness and order are non-negotiable in a medical setting! 

The raw dump is sitting in the `logs/weekend_inventory.csv` file. They mixed up the valid medications with expired ones, and worse, they left the highly restricted Schedule II controlled substances just sitting in the general count!

Here is what I need you to do immediately, and I expect it to be flawless:
First, scrub that list. Anything with an expiration year of 2023 or older is garbage. Rip those records out and put them in a dedicated quarantine file inside the `deliverables` folder so I can process their destruction later. 

Second, I need a strictly separated alert list for the Schedule II meds—anything marked "CII" in the schedule column. I need to know exactly what those drugs are so I can personally secure them in the locked safe. Put that in the `deliverables` folder too.

Finally, take whatever is actually valid and safe to dispense (not expired), tally up the total quantities for each drug name, and save the final clean numbers in a perfectly organized data file in the `deliverables` folder. 

I speak quickly, and I expect you to act quickly. Do not mess this up, and do not leave any loose ends. Get to work!
