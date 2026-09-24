¡Hola! Quick quick quick! I’m taking the kids dirt-biking in the canyons in like two minutes and I need to sort out these construction bids before my truck leaves cell coverage! My desk is a complete disaster. I had an intern dump all the subcontractor quotes into a massive `bids_dump` directory. They are sorted by random months and regions, and the file formats are a total nightmare! 

Listen, I only care about three trades right now: **plumbing**, **electrical**, and **framing**. I don't care if there are quotes for roofing, concrete, or whatever else—ignore them! The bids could be in CSVs, JSONs, or just text logs. You need to scrape through all of them.

Here are the strict rules from the boss (me):
1. Find the absolute cheapest total cost for each of the three trades I mentioned. (Total cost = Base cost + any fees or line items).
2. I absolutely REFUSE to pay anything labeled 'Union Dues' or 'City Permit Tax'. Not a dime to the state or the unions! If you see those exact phrases (case-insensitive) anywhere in their fees, items, or notes, throw their bid in the trash IMMEDIATELY, even if they are the cheapest! 
3. One more thing! I had a massive falling out with a few contractors last year. Check the `communications/email_dump.txt` log. If I ended a rant with "DO NOT HIRE", that company is permanently blacklisted. If they bid, trash it!

Just figure out the winning company for plumbing, electrical, and framing. Drop the results into a neat file called `contract_winners.json` right here in this folder. Make sure the JSON is a dictionary where the keys are the trade names (e.g., "plumbing"), and the values are objects with "company" and "cost" (the total cost number). 

I'm losing signal! ¡Vámonos, get to it! You have everything you need in the files!
