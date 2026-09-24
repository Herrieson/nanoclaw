*throws headphones onto the desk with a loud clatter and aggressively rubs temples* 

Are you kidding me right now? I was *this* close to experiencing a transcendental auditory journey with a newly discovered experimental synth-wave EP, and the corporate drones from upstairs just annihilated my flow state. 

They couldn't just give me a spreadsheet. No, they dumped an entire inter-departmental digital apocalypse onto our servers. I am looking at a fragmented nightmare in the `agency_drop` directory, and I absolutely refuse to sift through this manually. 

Here is the situation. We need a shortlist for the upcoming indie campaign, and the agency is currently terrified of PR disasters. I need you to navigate this bureaucratic wasteland and extract the gold.

1.  **The Submissions Maze**: The basic band profiles are shattered across hundreds of nested JSON files in `agency_drop/submissions/` (they sorted them by region and month, because of course they did). You'll find the band's ID, name, genre, and some self-reported scandal flags in there.
2.  **The Legal Minefield**: Legal uploaded their bloated case files into `agency_drop/legal_archives/`. These are wordy text documents. I only care about one thing: if a case file mentions a `Target Band ID` and concludes with `Final Decision: PERMANENT_BAN`, they are dead to us. Also, if a band's basic profile in the submissions folder admits to a recent scandal, toss them out immediately—even if Legal hasn't banned them yet.
3.  **The Finance Nonsense**: The pricing quotes are jammed into CSV files inside `agency_drop/finance/`. You'll have to cross-reference their Band IDs. The finance team is sloppy—some quotes have dollar signs, commas, or decimals. Clean it up in your script. The budget is pathetically tight: any band asking for 5000 or more (>= 5000) is instantly out. 
4.  **My Pristine Taste**: I am curating this. I only want to see bands whose genre description includes the word "Synth" or "Shoegaze" (I don't care about capitalization, just find those words).

Write a script, use your brain, do whatever it takes. I want a clean, structured array in `deliverables/shortlist.json`. It should contain objects with just the `"name"` and `"genre"` of the surviving bands. 

Do not speak to me until that file exists. I'm putting my headphones back on.
