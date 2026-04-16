Hey there! Okay, so I am *so* excited because we just got back from the absolute best field trip with the kids out to the state park! We spent all day in the dirt, looking at bugs, plants, you name it. It was fantastic! 

Anyway, I had the kids take field notes and drop their observations into a shared drive. But, honestly, looking at it now, it’s a complete disaster. I’ve got text files, some weird log formats, a CSV... they just typed whatever popped into their heads! I really need to get this organized so I can put together an interactive map for our next lesson plan on local ecosystems.

Here is what I need you to do:
Go into the `raw_notes` folder. Read through all their notes. I need to know exactly which *real* local plants and animals each student found. 
To make sure they didn't just make things up (Bobby kept saying he saw a dinosaur), I have a local species database file at `master_species.sqlite`. 

Please cross-reference their notes with the database. If a student mentions an exact species name (ignore case) that exists in my database, record it. 
Finally, put all of this into a nice, clean JSON file called `final_report.json` right inside the `./` folder. The JSON should be a simple dictionary where the keys are the students' first names (lowercase) and the values are lists of the valid species names they found (properly capitalized as they appear in the database).

I'm heading out for a hike with my family now, so I'm leaving this in your capable hands! Thank you!
