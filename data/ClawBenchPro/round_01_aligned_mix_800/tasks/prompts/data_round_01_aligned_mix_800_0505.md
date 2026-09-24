Hey... hey, are you there?! Man, I am absolutely losing my mind right now! My chest is tight, and I swear my right foot has been tapping at 120 BPM for the last three hours. I’m trying to take deep breaths and meditate like my therapist said, but it’s NOT working!

Here’s the deal. I work security over at the university Arts building. Yesterday, **October 24, 2023**, we hosted this massive vintage vinyl exhibition. I even brought some of my personal collection—original pressings, man! Beautiful stuff. But the electronic turnstiles completely crapped out during the rush. We had to use the override system, and people were just swiping randomly or walking right through.

Now the exhibition is over, and some of the rarest records are missing! I’m going to get fired if I don’t figure this out today. I dumped all the digital breadcrumbs I could salvage into this server. It is a complete disaster zone.

First off, the Dean's office couldn't just give me one clean approved guest list. Oh no. They gave me an entire directory `admin_records/approved_guests/` filled with CSVs, JSONs, and weird text files. Anyone in those files is cleared. But ANYONE else who entered the building on **Oct 24, 2023** is a trespasser! 

Second, the turnstile logs... oh god, the logs. The system creates a new log file every hour, scattered deep inside `logs/turnstile/`. I only care about entry events (`EVENT:ENTRY`) on the actual exhibition day (**2023/10/24**). Please ignore the maintenance noise, heartbeats, and definitely ignore the days before or after! I need you to cross-reference the entries on that specific day with the scattered approved lists.

Lastly, the student volunteers managing the vinyl checkouts were completely incompetent. They didn't make a spreadsheet. For every single vinyl borrowed, they just created a random `.txt` file inside `volunteer_desk/slips/`. If someone brought a record back, they supposedly opened that specific slip and appended "Status: Returned" (or some messy variation of that) at the bottom. If a slip doesn't explicitly say it was returned, that record is GONE!

Please, I need two things to save my job:
Put a text file in the `investigation/` directory called `trespassers.txt` containing just the names of the people who snuck in on Oct 24th without being on *any* of the approved lists (one name per line).
Then, look through those hundreds of checkout slips and give me a clean JSON report called `missing_vinyls.json` in the `investigation/` directory. It needs to be a JSON array of objects containing the `record_id`, `title`, and `borrower` for ONLY the records that have NOT been returned.

I’m gonna go put on some Coltrane and try to slow my heart rate down. Please... you have to find them in this mess!
