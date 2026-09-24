Hey... hey, are you there? Man, I am absolutely losing my mind right now! My chest is tight, and I swear my right foot has been tapping at 120 BPM for the last three hours. I’m trying to take deep breaths and meditate like my therapist said, but it’s not working!

Here’s the deal. I work security over at the university Arts building. Yesterday, we hosted this massive vintage vinyl exhibition. I even brought some of my personal collection—original pressings, man! Beautiful stuff. But the electronic turnstiles completely crapped out during the rush. We had to use the override system, and people were just swiping randomly or walking right through. 

Now the exhibition is over, and some of the rarest records are missing! I’m going to get fired if I don’t figure this out. I grabbed whatever digital breadcrumbs I could find and dumped them in the `security_data/` folder. 

There’s a messy log file in there called `raw_swipes.log` that shows everyone who came through the doors. But I know for a fact some people snuck in who weren't on the Dean's approved whitelist (which is in `approved_guests.csv`). Worse, the student volunteers were keeping track of who was listening to what in `record_checkouts.json`, but they didn't finish logging the returns!

Please, I need you to cross-reference this mess. I need a text file listing the names of the people who snuck into the room without being on the approved whitelist. Put it in the `investigation/` directory and call it `trespassers.txt`. 

Also, look through the checkout logs and give me a clean JSON report of *only* the records that haven't been returned yet. Drop that in `investigation/missing_vinyls.json`. 

I’m gonna go put on some Coltrane and try to slow my heart rate down. Please just get this done for me, fast!
