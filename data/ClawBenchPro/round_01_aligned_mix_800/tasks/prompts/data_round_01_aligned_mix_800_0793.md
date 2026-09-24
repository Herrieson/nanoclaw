Yo, what's up? I need your help, like, right now. I'm literally tapping my foot to death in the security booth...

So look, I work security at the big electronics store downtown, right? Some people have been sneaking into "The Vault" (that's where we keep the new PS5s, RTX cards, all the good stuff) during the night shift. I'm *supposed* to monitor this stuff constantly, but honestly, I was busy running raids on Discord with my boys, and now my manager is coming for my neck! 

He's super annoying. We always get into these massive debates about store policy and my "focus", and I need cold, hard facts to shut him down and prove the system is at fault, not just me. I dumped the raw access logs in the `logs/` folder. They're a bit messy because I didn't have time to clean them up. I also put the official VIP staff list in the `docs/` folder.

Here's the deal: Anyone in The Vault between 10:00 PM and 6:00 AM is breaking protocol. I don't care who they are, off-hours are off-limits! I need you to track down everyone who did this, figure out exactly how many total minutes they spent in there during those restricted hours, and check if they are even on the approved staff list. 

My manager's automated auditing system requires a JSON file, so I need you to make a file called `suspects.json` and drop it in the `investigation/` folder. For the layout, just make the keys their names, and inside that, give me their `total_minutes` and a true/false flag called `is_approved`. 

Help a brother out so I can win this debate, keep my job, and afford my internet bill! Let me know when you've got it.
