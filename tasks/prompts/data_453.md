Hey! I'm super stoked for our upcoming geo-tour. Fun fact: did you know Colorado actually has 58 mountain peaks exceeding 14,000 feet? We call them "Fourteeners." It's totally rad! 

Anyway, I'm in a bit of a gnarly situation with the admin side of things. I'm organizing this trip for the university, and the data is all over the place. My buddy from the IT desk dumped some portal logs for me, but it's a mess. 

Here's the deal:
I have a `students.db` SQLite database with the basic registration info (including whether they signed the liability waiver—super important, no waiver, no trip!).
But their dietary restrictions are stuck in a weird log file called `portal_dump.log`.

Can you hook me up with two things?
1. A clean `manifest.json` file. It needs to be a list of the students who are *actually going* (meaning they signed the waiver). For each of those students, I need their `id`, `name`, `emergency_contact`, and `diet`. 
2. A `catering_summary.txt` file so I can order the food. Just list the total count of each dietary requirement for the students who are going (e.g., "Vegan: 3", "None: 10").

Everything you need is in this directory. Thanks a million, man! See you on the trails!
