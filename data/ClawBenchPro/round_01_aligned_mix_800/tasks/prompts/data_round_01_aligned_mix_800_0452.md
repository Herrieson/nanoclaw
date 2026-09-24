Look, I'm literally pulling my hair out right now and I don't have the patience for a long back-and-forth. The massive storm just absolutely wrecked our family’s wilderness resort, and the volunteer groups’ offline sync system completely crashed. 

Instead of sending me a nice, clean CSV of the trail inspection logs, the system shattered the data into hundreds of fragmented files scattered across the `field_sync` directory. Half of these volunteers are rookies submitting "ghost data," and some don't even know how to write down a valid kilometer marker on their GPS!

My dad expects me to lead a trail clearing and camping expedition this weekend, but I can't even process this mess. He left a frantic text log in my `inbox` complaining about the rookies and some "standard hazard codes." I don't even know what version of the rulebook we are using anymore, but I think the old versions are still buried in the archives. You'll need to figure out what gear I should pack for each issue based on the warehouse manifest we keep in the `logistics` folder.

You know I need to see things visually before I head out into the woods. I need you to parse through that digital wasteland and figure out which sections are **critical hazards**—meaning anything with a severity of 8 or higher. Ignore the sections where the kilometer marker is garbled, "NaN", missing, or unreadable; I can't guess where those are. 

Here is what I need you to do, and please, just get it done:
Create a new folder called `planning`. Inside it, make me an `action_plan.md`. I need a clean, highly readable visual table in there showing only the critical hazards you filtered out (include Trail ID, KM, Issue, and Required Gear). 

Also, I'm plugging this into my dad's GPS software later, so I need a strict JSON file in that same folder called `gps_pins.json`. Just map the critical Trail IDs directly to their valid kilometer markers (as numbers) so the software can ingest it. 

There are hundreds of files. Don't try to read them manually. Write a script, read the clues, filter the noise, and just give me my plan. I'm incredibly stressed and just want to meditate instead of dealing with this, so please don't mess this up.
