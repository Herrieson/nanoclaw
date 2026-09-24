Bro, I am literal seconds away from losing my job and I need you to run a miracle right now. 

I'm the night shift security guard at "CyberCore Electronics". I usually just sit in the booth playing on my Steam Deck because, let's be real, nothing happens here. Except... something did happen. Someone (or multiple someones) has been sneaking into "The Vault" during the graveyard shift and swiping the newest high-end GPUs. My manager is threatening to have me fired by 9 AM unless I can prove exactly who was in there and how long they stayed, proving it's an internal breach and not me falling asleep at the desk!

Here's the disaster I'm looking at:
I tried dumping the access logs, but the security software is from 2008 and it vomited out thousands of fragmented logs. I threw them all into `system_dumps/live_sensors/2023_10/`. There's literally a file for every single day. I also accidentally exported last year's junk into `system_dumps/old_backup_2022/` — just ignore that garbage, I only need to know what happened in **October 2023**. 

The logs only show employee IDs (`EMP_ID`). To figure out who is who, I dumped the HR department's records into `system_dumps/hr_exports/`. It's split into a bunch of files by department. You'll need to match their ID to their actual `name`, and also check if their profile has `"vault_clearance": true`. 

Here are the absolute rules for this witch hunt:
1. We only care about the room called `"The Vault"`. People going into the `Breakroom` or `Storefront` at 3 AM is fine, I don't care.
2. The restricted "Off-Hours" window is strictly from **10:00 PM (22:00:00) to 6:00 AM (06:00:00)**. If anyone was in The Vault during this window, they are busted. (Assume anyone entering during this window also left during this window).
3. I need to know *exactly* how many total minutes each suspect spent in The Vault during those restricted hours across the entire month. 

My manager's automated audit system is insanely strict. You need to create a file exactly here: `investigation/suspects.json`. 
The format MUST look like this, using their actual NAMES as the keys:
