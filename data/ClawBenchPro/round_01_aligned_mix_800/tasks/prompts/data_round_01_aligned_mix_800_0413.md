*(rubbing temples, staring blankly at a sprawling directory tree on the monitor)*

I cannot believe this. I took a brief break from migrating enterprise clusters to coordinate our community church's regional volunteer drive, thinking it would be a walk in the park. My mistake. It is an absolute, unmitigated disaster. 

The background check department didn't just give me a clean roster. No, they dumped everything into the `bg_checks` directory. It’s a maze of folders organized by random regional codes, and it contains files for *everyone* who applied. We only allow folks whose status is explicitly marked as "approved". If they are "pending" or "rejected", they absolutely cannot serve!

And the site coordinators? I'm going to lose my mind. They dumped all their logs into `field_reports`. I specifically told them to only submit final reports. But look at it! It’s littered with `.bak` files and files with names containing `DRAFT`. I've told them a thousand times: I will *only* accept files whose names start with `FINAL_`. Everything else is unreliable noise and must be completely ignored.

To make matters worse, they used whatever format they liked—some CSVs, some JSONs with weird keys, and some plain text files where they just scribbled "Name: X | Time: Y". And the time units? Don't get me started. Some wrote hours, some wrote minutes (like "120 mins"). It's chaotic.

I need you to step in as my technical lead. Wrangle this mess and generate a precise JSON report. Place it in `deliverables/final_report.json`. 
I need exactly two things in that JSON:
1. `"total_approved_hours"`: A float representing the grand total of valid hours worked by our *approved* volunteers across all valid `FINAL_` reports.
2. `"gatecrashers"`: A list of names (sorted alphabetically) of anyone who logged time in a valid `FINAL_` report but is *not* an approved volunteer. I saw Gary sneaking around, and I need hard proof of who else gatecrashed.

I have to run and pick up my kids from soccer practice. Please, just figure out their messy formats, standardize the hours, filter the noise, and have that report ready before I get back. You’re a lifesaver.
