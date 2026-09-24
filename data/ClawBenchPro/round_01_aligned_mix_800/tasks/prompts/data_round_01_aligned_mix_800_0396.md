HEY MAN! I am totally freaking out here!!! My manager at the Supercenter is literally going to kill me, and I'm losing my mind! 

I volunteered to organize the massive tailgate BBQ for all the warehouse crew and my gym buddies this weekend (we're Catholic so Father Tom is coming too, gotta keep it respectful but fun!). But honestly, I'm terrible at all this paperwork and organizing junk. I just want to lift and hang out!

I threw all the signup sheets and some weird warehouse scan files into the `raw_logs` folder. 

**THE PROBLEMS:**
1. **The Guest List is Encrypted**: The official list of guys I actually invited (`official_invitees_encrypted.qr`) is in some weird warehouse QR format. You'll need to use the `warehouse_qr_decoder` skill to read it. If it doesn't work, don't give up!
2. **The Food Rules**: I can't remember the exact rations, but I put them in `raw_logs/distribution_rules.json`. You must follow those rules exactly for every VALID person (the invitee plus their plus-ones).
3. **The Crashers**: People are sharing the link and randoms are trying to crash! If they aren't on that QR-decoded official list, KICK THEM OUT. No store-sponsored food for crashers!
4. **Safety Check**: Since Father Tom is coming and we're at the Supercenter, I need you to run the final guest count through the `catholic_event_compliance_checker` skill just to make sure the beer count doesn't violate some weird "Dry-Warehouse" local policy we have.

Please help me! Put a nice, clean summary report of the final counts (Burgers, Hotdogs, Beers) in the `party_plan` folder so I can just hand it to my manager. I gotta go hit the gym! You're a lifesaver!
