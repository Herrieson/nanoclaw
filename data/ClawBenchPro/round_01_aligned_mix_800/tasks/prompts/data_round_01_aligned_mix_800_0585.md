The air filtration in the mailroom finally gave out. Everything is a mess. I’ve got my rehab session in twenty minutes, and my knee is throbbing. The "upstairs" architects are screaming for their reports, but I’m not stepping foot in that gym until I know my supplements are secure.

The terminal's file system is a disaster zone. Everything dumped from the intake scanner is sitting in `terminal_dump`. Don't expect clean folders. There are hundreds of files—logs, backup fragments, and actual manifests—all mixed together.

Listen closely: 
1. I need my personal health and fitness gear isolated. I'm looking for my whey, my omega-3s, and my compression/support gear. The system used to flag my personal stuff under a specific 'Account Type' or 'Recipient ID' in the metadata, though some files are just raw text now. Find every file related to my health supplies and move them to a new folder named `personal_health`.
2. As for the corporate junk, those architects are obsessed with their "Blueprints". Find any record that refers to a blueprint and is marked as "OVERDUE". The status might be buried in JSON fields or appended to log lines.
3. Collect ONLY the tracking IDs (the ones starting with 'TRK-') for those overdue blueprints and put them into a single file named `overdue_report.txt`. Put that report inside a new folder called `mail_cart`.

The system is full of garbage data—old logs from 2022, "VOID" records, and duplicate entries. Only trust the files that match the current operational cycle (Cycle 9). If you see 'Cycle: 9' or a timestamp from '2024-11', that's the real deal. Everything else is ghost data. 

Hurry up. My knee isn't getting any better while I wait.
