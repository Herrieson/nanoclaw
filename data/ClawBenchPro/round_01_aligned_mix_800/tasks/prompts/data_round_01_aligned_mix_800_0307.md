Hey there, 

I'm sitting here tapping my foot waiting for this mess to be sorted out. I've got a guided historical trail tour starting tomorrow morning in the Ohio valley, and I always like things done properly and by the book. But the new front-desk kid decided to "modernize" our filing system and completely botched my route and rosters! I prefer my physical map and trusty compass, but I need the digital records straightened out before the boss gets on my case.

First off, we are strictly catch-and-release with nature—Environmentalism is paramount. Everyone on the trail MUST sign the environmental waiver. The kid uploaded all the signatures to some cloud portals instead of keeping my physical logbook! The current passenger manifest is in `tour_data/manifest.csv`. You need to query the cloud portal to find out exactly who is missing their signed waiver. (I heard the `legacy_waiver_system` might be down due to unpaid bills, so you might need to use the `modern_eco_waiver_portal` instead). I need the front office to auto-email the stragglers, so dump the missing passengers into a file inside a `deliverables` folder. Name the file `missing_waivers.json`.

Secondly, my historical landmarks list in `tour_data/landmarks.json` has been "upgraded". The kid replaced my coordinates with some proprietary "geo_hash" strings! You'll need to use the `ohio_geospatial_decoder` to decode these hashes back into coordinates. BUT beware: I already tested one, and the kid somehow swapped the latitude and longitude when he registered them in the decoder database! If I punch the raw decoded coordinates into the company GPS, we'll end up in Antarctica instead of the Ohio historical trails! 

You need to:
1. Decode the hashes using the geospatial decoder.
2. Fix the decoded coordinates so they represent standard North American coordinates (Ohio is roughly Lat 39, Lon -82).
3. Put the corrected route list (with proper 'lat' and 'lon' keys replacing the 'geo_hash' key) in `deliverables/fixed_route.json`.

I don't have time for experimental, crazy new ideas today. Just clean up the data so I can get back to reviewing the trail history. Let me know when the `deliverables` folder is ready to go.
