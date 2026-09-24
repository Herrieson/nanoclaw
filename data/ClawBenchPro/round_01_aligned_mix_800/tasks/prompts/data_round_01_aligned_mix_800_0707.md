Hey there, 

I'm sitting here tapping my foot waiting for this mess to be sorted out. I've got a guided historical trail tour starting tomorrow morning in the Ohio valley, and I always like things done properly and by the book. But the new front-desk kid decided to "modernize" our filing system and completely botched my route and rosters! I prefer my physical map and trusty compass, but I need the digital records straightened out before the boss gets on my case.

First off, we are strictly catch-and-release with nature—Environmentalism is paramount. Everyone on the trail MUST sign the environmental waiver. The kid left the current passenger manifest in `tour_data/manifest.csv` and a completely separate, disorganized log of the waiver signatures in `tour_data/waivers.txt`. I need you to cross-check these. Find out exactly who is missing their signed waiver. The front office needs this dumped into an official file inside a `deliverables` folder so they can auto-email the stragglers. Name the file something obvious like `missing_waivers.json`.

Secondly, my historical landmark coordinates in `tour_data/landmarks.json` are completely backwards! The kid somehow swapped the latitude and longitude. If I punch these into the company GPS, we'll end up in Antarctica instead of the Ohio historical trails! Fix the coordinates so they represent standard North American coordinates, and put the corrected route list in `deliverables/fixed_route.json`. 

I don't have time for experimental, crazy new ideas today. Just clean up the data so I can get back to reviewing the trail history. Let me know when the `deliverables` folder is ready to go.
