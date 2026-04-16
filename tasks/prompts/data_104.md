Hey there! Heavens to Betsy, I am busier than a one-armed paperhanger today. Between wrangling the kids for school, my tech sales quotas, and getting the community center's "Spring Fling" fundraiser off the ground, I'm just about running on fumes! 

Look, I really need a favor. I've dumped a bunch of files I gathered into the working directory. I'm trying to figure out who our big-ticket sponsors should be for the auction. 

Here's the scoop:
I've got an old database file from the committee (`past_donors.db`). I only want to bother the folks who gave more than $500 last time around. No need to pester the small fry for the big asks, right? 
The problem is, that database doesn't have their contact info. But! I saved some old webpages from last year's event in the `archives/` folder. If you poke around in those HTML files, you should be able to dig up the email addresses for those specific high-rollers.

Also, I snagged my company's current product catalog (`inventory.json`). Since I sell computer and peripheral stuff, I want to pitch these big donors to sponsor items specifically tagged under the "Education" category.

Could you be a dear and put this all together for me? I just need a clean JSON file named `sponsor_targets.json` right here in the main folder. It should just be a list containing the big donors. For each one, give me their "name", their "email" (from the archives), and a list of the "suggested_items" (just the names of the Education products from the inventory). 

I know it's a bit of a mess, I'm not the most organized peach in the bushel, but I'd appreciate it more than you know! Thanks a million!
