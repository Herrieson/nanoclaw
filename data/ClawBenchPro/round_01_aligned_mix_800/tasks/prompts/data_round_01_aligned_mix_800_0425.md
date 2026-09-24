Oh my gosh, hello! Sorry if this message is a total mess, I am literally typing this one-handed while bouncing my teething toddler on my knee! 😭

You are an absolute lifesaver for helping me. Our clinic’s IT volunteer, Greg, thought it would be a "great idea" to upgrade our volunteer tracking system last month, and now EVERYTHING is completely fragmented! I am completely overwhelmed and I just need two simple things for my funding meeting tomorrow, but the data is a nightmare.

Here is the situation:
Greg dumped the new system's logs into a folder called `sys_logs/`. It's a disaster—every day has its own folder, and for some reason, he mixed CSV files and JSON files! What even is that?! Worse, we have a `legacy_archive/` folder floating around in the workspace from 2010—PLEASE completely ignore that folder, it will ruin all our current numbers. 

The old `whitelist.txt` is dead. Now, everyone has a weird digital clearance file in `admin/clearances/`. Only the ones that specifically say their status is "ACTIVE" are actually approved to be here. Some are "REVOKED" or "PENDING", which means they shouldn't be volunteering! But I’m terrified that some of these unapproved people (or worse, people who don't even have a clearance file) have been sneaking in and logging hours in `sys_logs/`. 

Also, they replaced all the family descriptions in the logs with stupid codes like "F-something". I think there's a dictionary or mapping file in the `config/` folder that explains which code means what. 

Could you please write a script to dig through this mess and give me a summary? I created an empty `reports/` folder. Please put a file called `final_report.json` in there with exactly these two keys:
1. `"unauthorized_names"`: A list of the ACTUAL NAMES of anyone who logged hours in `sys_logs/` but isn't on the active clearance list. (You can't just give me their ID numbers; I need their real names. Greg left a master directory somewhere in the `admin/` folder, I think).
2. `"under_5_approved_hours"`: The total valid hours spent helping families with children "Under 5", but ONLY count hours from our officially ACTIVE volunteers! And please, if there are hours that say "N/A" or are negative, just skip them—obviously you can't work negative hours!

Thank you, thank you, thank you! I have to go stop my kid from eating a crayon, you're the best!
