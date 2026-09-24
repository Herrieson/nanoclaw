Oh my goodness, Namaste! I am completely dysregulated and my anxiety is through the roof right now! 

I'm organizing the Diwali Bake-and-Cook Sale fundraiser for our school—I even taught some of the kids how to make proper samosas! But my scaffolding for the data collection was completely inadequate, and now it's a massive, fragmented disaster. I am definitely lacking in the conscientiousness department today!

Our principal needs the final formative assessment of our volunteer hours in the next hour, and I'm supposed to be practicing yoga to manage my stress! I need you to help me get back to baseline.

Here is the chaotic situation:
1. **The Roster Nightmare**: The initial official student list is stuck in `administration/roster_v1.json`. But it's outdated! We had kids transfer in and drop out, and my assistant just threw a bunch of messy text files into the `administration/amendments/` directory. You must apply every single `ADDED: <Name>` and `REMOVED: <Name>` from those amendment notes to the v1 roster to figure out who is ACTUALLY on the final official roster.
2. **The Log Explosion**: The volunteer logs are scattered everywhere inside the `raw_logs/` directory. There are dozens of subfolders. Some are JSONs, some are CSVs, and some are just weird TXT notes. 
3. **Toxic Noise**: My past self was super unhelpful and left a lot of trash. Please IGNORE any file or folder that has `draft`, `backup`, or `deprecated` in its name (case-insensitive). They are completely invalid and will poison our data!
4. **Parent Slips**: The kids wrote all kinds of random things for their parent slip status. To be safe, if their slip status simply starts with the letter 'y' or 'Y' (like yes, yep, yea, Y), consider it approved. Anything else is unapproved.

I only want to count the hours of students who are **actually on the final amended roster** AND who **have an approved parent slip**. 

Can you please calculate the total valid volunteer hours for me? Also, I need to know exactly who the "problem" students are—anyone who logged hours but either wasn't on the final official roster, or didn't have a valid parent slip. 

Please put your final report in the `deliverables/final_report.json` file. The principal's system needs it to be a valid JSON containing exactly two keys:
- `"total_valid_hours"`: (integer) the sum of all approved hours.
- `"flagged_students"`: (a sorted list of strings) unique names of the problem students so I can have a restorative circle with them later.

Thank you so much! Please hurry, I need to start my deep breathing exercises!
