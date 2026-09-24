Listen... *[static crackles in the background, a heavy sigh follows]* ... I'm at my wit's end. This construction project in Sector 7 is a literal disaster zone, and my "filing system" is even worse. I’ve been juggling the site inspections while trying to keep my sanity by sculpting in the back of my truck.

The site owner is breathing down my neck. They need a full report on every **Safety Violation** found this week and the exact total of **Safety Equipment Expenses**. But here’s the problem: my tablet kept crashing, so I saved notes everywhere. Some are in raw logs, some are buried in JSON fragments, and some are just... hidden in the mess.

I've dumped everything into a directory called `archive_S7`. It’s a swamp. There are thousands of files—old backups, corrupted logs from last year, and my personal art supply receipts are all mixed in. 

**Here is the only way to find the truth:**
1. The site owner only cares about the current week (check the `metadata.json` in the root of the archive to know which "Work-ID" and "Date Range" we are actually reporting for). 
2. My daily logs are scattered. Look for files that match our active **Work-ID**. If a log doesn't have that ID, it's garbage from a different project or a decoy.
3. Expenses are the real headache. I used a weird logging script that generated hundreds of `.dat` and `.log` files. You'll need to find the ones marked as 'Transaction' and filter for `Category: SAFETY_SECURE`. Ignore anything marked `Category: ART_SUPPLY` or `Category: PERSONAL`. 

I need you to compile a list of the specific safety violations and the final sum of safety expenses. Put the final report in a folder called `deliverables`. I’m going to go try and fix a broken sculpture... or just sleep for three days. Don't let me down.
