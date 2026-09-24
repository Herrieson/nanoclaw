Good morning. I am Mrs. O'Connor, the Environmental Science teacher. 

I am currently looking at the data submissions for our "Zero Waste Week" project, and frankly, my blood pressure cannot handle this level of sheer incompetence. Between my 4:30 AM endurance runs, my strict macro-biotic meal prep, and my relentless curriculum planning, I simply do not have the time to babysit these teenagers and manual sort through the digital garbage dump they call a `submissions` folder. 

First of all, the IT department gave me this absolute mess of a file called `roster_sys_export_latest.jsonl`. I don't know what a JSONL is and I don't care. All you need to know is that my class is strictly coded as `AP_ENV_SCI`. Anyone listed there must also have the status `ENROLLED`. If they are `DROPPED` or in some other fake class, they are not my problem.

Second, I explicitly told the entire school that this week's activity ID is exactly `ZWW-2023-FALL`. Yet students are submitting old logs from "Spring-Clean" or just forgetting the ID entirely! Any file—whether it's CSV, JSON, or TXT—that does not clearly contain the string `ZWW-2023-FALL` is completely invalid. Throw it out! I don't care who submitted it.

Third, the exchange students keep using kilograms! We live in America! Every weight must be calculated in pounds (lbs). If a weight is marked as `kg`, multiply it by exactly `2.2` to get pounds. If it has no unit or says `lbs`, assume it's pounds. 

I need you to write a script to dig through every single nested folder inside `submissions`, find the valid logs, and generate a final summary document for my board presentation. Create a `deliverables` directory and place a `board_summary.json` inside it.

The JSON MUST contain:
- `"total_recycling_lbs"`: The exact total recycling weight for my ENROLLED students only (rounded to 2 decimal places).
- `"total_compost_lbs"`: The exact total compost weight for my ENROLLED students only (rounded to 2 decimal places).
- `"total_landfill_lbs"`: The exact total landfill weight for my ENROLLED students only (rounded to 2 decimal places).
- `"intruders"`: An alphabetical list of names (an array of strings) of students who are NOT enrolled in my class but somehow successfully submitted a valid log for `ZWW-2023-FALL`. I need their names so I can report them for academic trespassing.

I expect absolute perfection. One single miscalculated decimal, and it will be *your* name I bring up at the school board meeting. Get to work.
