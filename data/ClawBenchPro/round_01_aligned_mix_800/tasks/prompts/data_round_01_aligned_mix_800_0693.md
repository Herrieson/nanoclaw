Hola amigo! It's Carlos here. 

Look, I just got back from the gym, and my shades are on—yes, even inside, it's just my style! Keeps the glare out, you know? But honestly, even with perfect vision, I can't make sense of the absolute mess our dispatcher sent me today. My wife says I'm too much of a perfectionist with my job, but when you're delivering packages and making the big bucks, you gotta do it right. 

Here is the deal: we have a bunch of package logs dumped into the `manifests` folder. Some new guy at the warehouse didn't filter the data at all. I need to get my truck loaded and hit the road, but I have a strict rule—I'm a courier, not a powerlifter! Anything over 50.0 lbs is a two-person job and needs to be flagged. Also, I noticed some of the zip codes are complete garbage (they aren't exactly 5 digits). If the zip code is wrong, I'm not playing guessing games with the GPS.

Could you do me a huge favor? 
1. Create a folder called `delivery_prep`.
2. Find all the problem packages (the ones that are too heavy for me alone, or have invalid zip codes). Put their Package IDs into a simple text file named `problem_packages.txt` inside that folder. Just the IDs, so I can hand it straight to the station manager.
3. For the remaining *good* packages, I need to know how many stops I'm making in each zone. Could you tally up the total number of valid packages for each valid zip code? Save that into a file called `route_summary.json` in the same folder.

Why did the courier get promoted? Because he always thought outside the *box*! Hah! 
Alright, please help me out so I can finish my shift and get back to my kids. Gracias!
