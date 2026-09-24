I... I think I've ruined everything. My English portfolio is due in an hour and my laptop just... died. I've managed to recover the `archive` folder, but it's a complete nightmare. My ADHD got the better of me and I started organizing things by date, then by mood, then by "vibe"... everything is scattered across dozens of subdirectories.

I need you to salvage the final, English-only poems. Please, you have to be careful. I have hundreds of files in there, but most of them are garbage—old class schedules, grocery lists, or those "venting" sessions where I just type "nervous" over and over again. And my Abuela's Spanish poems are mixed in too; she'd love them, but my English teacher definitely won't.

Here's the only way to find the "real" ones:
1. They are definitely in `.txt` or `.log` files (I was desperate), but ignore anything with "draft", "todo", or "fix" in the filename.
2. Inside the file, a finished poem MUST have a structured header like `[STATUS: FINAL]` and `[LANG: EN]`. If it says `[STATUS: DRAFT]` or `[LANG: ES]`, skip it.
3. If the content contains the words "TODO", "nervous", or "fidgeting", it's a venting file, not a poem. Throw it out even if the header looks okay.
4. I often saved multiple versions. If you find poems with the exact same title, only keep the one with the latest "Last Modified" timestamp (you'll need to check the file's metadata).

Please gather all these final English poems into a single JSON file called `final_portfolio.json` inside the `submission` folder. The JSON should be an object with a "poems" key (a list of objects with "title", "content", and "line_count") and a "grand_total_lines" key (the sum of all lines across all selected poems). 

I'm shaking just thinking about failing this class. Please help me.
