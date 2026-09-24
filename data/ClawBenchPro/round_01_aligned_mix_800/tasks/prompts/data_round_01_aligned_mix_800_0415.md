God give me patience because if I have to look at one more disorganized spreadsheet, I am going to lose it. 

I'm Margaret. Since the flood hit the administrative wing at St. Jude’s, our record-keeping has descended into absolute anarchy. The new batch of "digital volunteers" we recruited are more of a hindrance than a help. They’ve managed to scatter our maintenance logs across dozens of subdirectories, mixed in with corrupted backup files, system logs, and "draft" notes that should have been deleted months ago.

I need a definitive audit, and I need it now. You'll find a chaotic mess in the `archive_root` directory. Somewhere in the `policy_vault`, there is a master whitelist of approved vendors—but knowing those volunteers, they probably split it into multiple fragments or hid it in some YAML configuration file. 

Your mission:
1. Sift through the `archive_root` and its deep subfolders to find all valid maintenance records. Ignore the "temp", "corrupted", or "test" files—only the actual work logs matter.
2. Cross-reference every contractor found in those logs against the official whitelist. 
3. Identify the "rogue" contractors—those who performed work but aren't on our approved list. Names might be mangled with erratic capitalization, leading/trailing whitespace, or even slight typos in the logs (though the whitelist is the "truth").
4. Calculate the total cost of all work performed ONLY by approved vendors, precisely to two decimal places.

The accounting team won't even look at this unless it's in a structured JSON file. Save your final report as `audit_report.json` in the `deliverables` folder. It must contain a list of `unapproved_contractors` (unique names, cleaned) and the `total_approved_cost`.

Don't come back to me asking where the files are. If you can't navigate a simple directory tree and handle a little bit of noise, you're of no use to St. Jude’s.
