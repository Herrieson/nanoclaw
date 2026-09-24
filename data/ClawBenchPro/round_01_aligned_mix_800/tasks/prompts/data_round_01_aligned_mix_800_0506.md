*takes a long sip from my reusable water bottle, rubbing my temples as I stare at the screen*

Hey... look, I really need someone to step in here. My social battery is completely fried. I spend all day at the retail job slapping on a fake smile, and honestly, as an extreme introvert, it drains the very life out of me. *waves hands emphatically* I just want to sit in my backyard, read my sci-fi novel, and pretend the rest of the universe doesn't exist.

But I made the mistake of promising my nieces that I’d organize the community garden's spring seed swap and volunteer drive. Protecting the local ecosystem is the only thing I care about more than being left alone. 

Our neighborhood’s online signup system is an absolute nightmare. Instead of a single spreadsheet, it puked out hundreds of separate data fragments scattered all over the `garden_data/signups/` directory, broken down by years and zones. 
Listen carefully: I **only** care about this year's event, meaning the `2024` folders. And honestly, neighbors are so flaky. Half of them clicked cancel right after signing up, so only look at the ones with a `CONFIRMED` status. To make matters worse, some people submitted the form multiple times because they forgot what they requested. If you see the same name more than once, just use their absolute latest submission based on the timestamp.

Then there's the invasive species problem. *shudders* I refuse to hand out a single seed of anything that doesn't belong here. I downloaded the county’s ecological guidelines into `garden_data/eco_policies/`. The county clerk is a mess and left a bunch of old drafts in there—ignore them. Just find the file that actually has `official` in the name to see what's banned. If a neighbor’s final, confirmed request asks for *anything* on that official invasive list, they are entirely banned from the swap. Kick them out. 

I don't have the energy to do the math. For the remaining people who actually passed this ecological purity test, figure out their total pledged hours. Some idiots literally typed words like "five" or "N/A" instead of numbers for their hours—just count those nonsense entries as 0 hours. 

I need you to generate a neat report in a new folder called `garden_deliverables/` named `summary.json`. It needs exactly two keys:
1. `approved_names`: A list of the names of the approved people (please, sort it alphabetically so my brain doesn't itch).
2. `total_valid_hours`: The total sum of their valid hours.

Please, just get it done. I’m going to go hide in the greenhouse.
