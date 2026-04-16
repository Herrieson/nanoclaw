Hello there. My name is Eleanor. I teach middle school at a lovely private non-profit academy here in New York. 

I'm currently trying to organize our annual "Nature & Empathy" student art showcase. It's a wonderful event—I actually spend a lot of my own free time sketching and gardening, so I know how important it is for the children to connect with nature and express themselves. 

Unfortunately, our school's computer system had a bit of a hiccup, and the files I downloaded are a dreadful mess. I have three files in the `school_data` folder:
1. `submissions.csv`: This has the student names, their grade, and the title of their artwork. But some rows are corrupted—either the grade is completely missing, or the art title contains the word "ERROR" or "CORRUPTED". We absolutely cannot include those entries; I'm highly organized and I want this to be perfect.
2. `directory.txt`: This is an old text dump from our staff portal. It has the parent contact emails for the students, but the formatting is all over the place.
3. `opt_out.log`: A server log showing families who have opted out of our mailing list. It is very important we respect their privacy and empathy dictates we do not email them.

I need you to look through these files and figure out exactly who we should invite. Please create a file named `final_invites.json` in my main folder. It needs to be a clean JSON list containing objects with exactly these three details: `student_name`, `email`, and `art_title`. 

I'm afraid I don't know much about coding—I usually use hand gestures to explain things, not keyboards!—so I'll leave it to you to figure out how to match everything up and filter out the bad data and the opt-outs. Thank you so much for your help.
