Hey there, friend! *waves hands enthusiastically, wiping grease on a rag* Man, am I glad to see you. I really could use your brains on this one. 

I'm just a simple guy in jeans and boots, usually operating the heavy machinery on site. But since my disability left me out of the cab, I've had a lot of free time. To keep busy, I'm heading up the church's community repair weekend. I love helping folks out, but honestly, this digital paperwork nightmare is driving me totally insane!

We had a web portal, a phone hotline, and offline sign-ups. When the IT kid exported it, he just dumped EVERYTHING into a folder called `signups_dump`. There are literally hundreds of files buried in sub-folders in there. Some are `.json`, some are `.csv` (which look like they use `|` instead of commas, go figure), and a ton of useless `.bak` or `.tmp` files that are just computer garbage. I can't look through this by hand!

Here is what I need you to do before the committee meeting tonight:

**First**, I need a list of everyone who is bringing a "truck" or a "backhoe" (it doesn't matter if it's capitalized or not, just if those words are in their equipment description). Just their names, one per line, in a file called `heavy_equipment_volunteers.txt` inside a new folder called `planning`. 

**Second**, I need the total man-hours promised by everyone. Just put the final number in a file called `total_hours.txt` in that same `planning` folder.

**But wait, here is the catch—Safety First!**
1. Some folks cancelled. If their `status` is marked as `withdrawn` or `cancelled` in their signup record, DO NOT count their hours and DO NOT put them on the equipment list.
2. The insurance company did an audit, and they left a bunch of log files in the `compliance_audits` folder. Any log that has the exact tag `[CRITICAL_VIOLATION]` means the worker listed right after it is permanently banned. 
The problem? The logs only show their ID (like `WorkerID: W-1234`). You'll have to match those IDs against the `master_roster.json` file in the main folder to find their actual names. If a person's name corresponds to a banned ID, DO NOT count their hours, and absolutely DO NOT put them on the equipment list, no matter what they are bringing!

I know it's a huge mess, but I figure someone smart like you can write a script to chew through all these folders and piece it together. I really appreciate you doing this for me. God bless!
