Hola amigo! It's Carlos here. 

Look, I just got back from the gym, and my shades are on—yes, even inside, it's just my style! Keeps the glare out, you know? But honestly, even with perfect 20/20 vision, I am going completely blind trying to make sense of the absolute garbage dump the warehouse dispatcher sent me today. My wife says I complain too much about the IT guys, but when you're delivering packages and trying to make a living, you need clean data.

Here is the nightmare: instead of one nice list, they dumped thousands of package records into the `manifests` folder. It's split by warehouses, dates, and they used CSVs, JSONs, and even some weird text files separated by pipes `|`. And listen to me—some of these folders are named with `void`, `backup`, or `test`. DO NOT TOUCH THOSE! If a folder has any of those words in its name, ignore everything inside it. It's old trash data.

To make matters worse, I found a file called `cancellations.txt` inside the `system_logs` folder. If a Package ID is in that file, the order is dead. Cancelled. Kaput. Pretend it doesn't exist at all. Do not flag it as a problem, do not count it as valid. Just ghost it.

Now, for the packages that actually matter, I have a strict rule—I'm a courier, not a powerlifter! Anything over 50.0 lbs is a two-person job and needs to be flagged. But guess what? The new international shipping guys mixed up the units! Some weights are just numbers (which means pounds, `lbs`), but some are explicitly tagged as `kg` or `oz`. I am not a scientist! Just remember this math: 1 kg = 2.20462 lbs, and 1 oz = 0.0625 lbs. If the weight converts to strictly more than 50.0 lbs, it's a problem package.

Also, the zip codes. Dios mío. Some of them have spaces around them, some are random letters, some are too long. A zip code is only valid if, after cleaning up the spaces on the edges, it is exactly 5 numbers. Nothing else. If it's garbage, the GPS will send me into a lake. Flag it!

Could you do me a huge favor and write a script to sort this out? 
1. Create a folder called `delivery_prep`.
2. Find all the **problem packages** (the ones that are too heavy for me alone, or have invalid zip codes, excluding the cancelled ones). Put their Package IDs into a simple text file named `problem_packages.txt` inside that folder (just the IDs, one per line, order doesn't matter, but please don't duplicate them).
3. For the remaining **perfectly good packages**, I need to know how many stops I'm making in each zone. Tally up the total number of valid packages for each valid zip code, and save that into a file called `route_summary.json` in the same folder.

Why did the courier get promoted? Because he always thought outside the *box*! Hah! 
Alright, please use your programming magic so I can finish my shift and get back to my kids. Gracias!
