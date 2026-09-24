Brother, thank God you're here. Look, I need a massive favor. 

*clears throat, speaking in a slow, stressed, resonant voice* 
I'm running the crew down at the new municipal build, and man, my head is completely fried. Between overseeing the foundation pours, making sure my little ones aren't burning the house down, and trying to finish this massive abstract canvas I've been painting in the garage... my paperwork has become an absolute nightmare. 

The city inspector is breathing down my neck for the weekly safety report for **the week of October 16th to October 22nd, 2023**. I used to keep neat site notes, but my stupid cloud dictation app updated and completely broke. Now, it just dumps every single voice memo I dictate—whether I'm on site, in the car, or at home—into a massive, deeply nested maze of scattered JSON files in the `voice_memos` directory. 

I need you to wade through that digital garbage dump and build a proper, formal safety report. 
Here is what you have to figure out:
1. First, you need to find the actual system project code for the "New Municipal Build". I think HR left a master project registry somewhere in the `admin_docs` folder.
2. Sift through the audio transcripts for that specific week and project. 
3. The dictation AI automatically slaps a `[SAFETY_VIOLATION]` tag on anything that sounds like a problem, and a `[HOURS=X]` tag when I mention billing time. Tally up the total man-hours my crew put in for that specific week.
4. Dig out all the *actual, genuine* construction site safety violations for that week. Filter out my ramblings—the inspector doesn't need to know about my toddler trying to eat my art supplies or me tripping over my canvas. I left a memo from the city in `admin_docs` that specifies exactly what counts as a real OSHA violation.

Once you extract the real safety issues and calculate the total hours, organize it into a clean JSON file. Name it `official_safety_report.json` and drop it into the `deliverables` directory. The format should just be `{"total_man_hours": 0, "safety_violations": ["issue 1", "issue 2"]}`. 

I'm trusting you with this so I can go spend some time with the kids before I lose my mind. Appreciate you.
