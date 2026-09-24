HEY MAN! I am totally freaking out here!!! My manager at the Supercenter is literally going to kill me, and I'm losing my mind! 

I volunteered to organize the massive tailgate BBQ for all the warehouse crew and my gym buddies this weekend (we're Catholic so Father Tom is coming too, gotta keep it respectful but fun!). But honestly, I'm terrible at all this paperwork and organizing junk. I just want to lift and hang out!

The problem is the RSVP link leaked on the store's intranet, and now HUNDREDS of random cashiers, corporate suits, and weirdos from other branches are trying to crash my party! I dumped all the messy RSVP data from the web portal into the `messy_rsvps` folder. It's a complete disaster. It's split into a ton of subdirectories, and some guys submitted the form multiple times because they kept changing their minds about how many "plus-ones" they were bringing, or they just cancelled entirely. 

Here's the deal, I ONLY want the guys on my OFFICIAL whitelist to get food. I backed up all my phone chats into the `phone_backup` folder. You'll have to dig through my messy group chat histories to find the final, undeniable whitelist (I think I yelled "FINAL BBQ WHITELIST" or something when I posted it). Ignore any draft lists I sent before that!

Once you filter out the crashers, figure out how many REAL people are coming (that's the invited guy PLUS their extra guests). But wait, some guys updated their RSVPs! If someone submitted multiple times, you MUST only count their most recent update based on the timestamp. And obviously, if their latest status says they cancelled, don't count them!

Also, my brain is fried and I completely forgot the exact amount of food to order per person. The store manager insists we follow the official "Catering Standard Protocol" for a Tailgate BBQ. I dumped the entire corporate policy database into the `store_policies` folder. It's like 500 files of boring garbage, but the food ratio is hidden in there somewhere.

Please, please, PLEASE calculate everything and write a JSON file to `party_plan/final_counts.json`. I need exactly these keys in the JSON: `total_valid_attendees`, `burgers`, `hotdogs`, and `beers`. 

I gotta go hit the gym to blow off this stress before my shift ends! You're a lifesaver!
