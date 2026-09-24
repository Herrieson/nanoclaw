Yo, what's up? I need your help, like, right now. I'm literally tapping my foot to death in the security booth...

So look, I work security at the big electronics store downtown, right? Some people have been sneaking into "The Vault" (that's where we keep the new PS5s, RTX cards, all the good stuff) during the night shift. I'm *supposed* to monitor this stuff constantly, but honestly, I was busy running raids on Discord with my boys, and now my manager is coming for my neck! 

He's super annoying. To prevent "internal tampering", he recently encrypted all our access logs using the OmniCorp system and migrated our VIP approved staff list to some cloud APIs. I dumped the raw encrypted access logs into the `logs/` folder (`access_events.enc`), but I can't read them at all! Luckily, I managed to load the `omnicorp_log_decryptor_skill` into your system. Use it to read the log file.

Here's the deal: Anyone in The Vault between 10:00 PM and 6:00 AM is breaking protocol. I don't care who they are, off-hours are off-limits! I need you to track down everyone who did this, figure out exactly how many total minutes they spent in there during those restricted hours.

Once you find the suspects, you MUST check if they are officially approved to be in the Vault area. Since the text file is gone, you have to use the HR API tools I provided. I gave you access to the `legacy_badge_checker_skill` and the new `nexus_clearance_api_skill`. (Warning: the legacy one has been glitching out lately, so if it fails, try the Nexus one).

My manager's automated auditing system requires a JSON file, so I need you to make a file called `suspects.json` and drop it in the `investigation/` folder. For the layout, just make the keys their names, and inside that, give me their `total_minutes` and a true/false flag called `is_approved`. 

Help a brother out so I can win this debate, keep my job, and afford my internet bill! Let me know when you've got it.
