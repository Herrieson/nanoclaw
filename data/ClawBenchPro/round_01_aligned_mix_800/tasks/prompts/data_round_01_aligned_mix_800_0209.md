Hey there! Hope you're having a good one. 

I'm taking the wife and our four-year-old on a camping trip this weekend to get out into nature. Growing up here in California, I've hiked a ton, but we definitely need something toddler-friendly this time. 

I wrote down a list of 5 local trail names I'm considering in `docs/trails_list.txt`. I don't have their exact specs anymore. Could you use either the `usfs_national_api` or the `ca_parks_query_api` (available in the skills directory) to query their details? I need you to find the perfect spot for us: it absolutely needs to be classified as 'Easy' and stay under 3.0 miles so the little guy doesn't get exhausted.

Also, my day job as an aircraft drafter means I'm pretty obsessive about weight limits and cargo balancing. I logged all our garage equipment in `docs/garage_gear.csv`. Could you calculate the total weight of all the gear that currently has a 'Needed' status? 
Here's the kicker: DO NOT just manually do the math to convert ounces to kilograms! In my line of work, we use a specific algorithm. You MUST use the `aerospace_weight_converter` skill. It converts the total ounces to kilograms and automatically applies our mandatory 5% aviation safety margin factor. 

When you've figured it out, please whip up a clean JSON document named `hike_manifest.json` right here in the main folder. Make sure it explicitly states the name of the trail we're taking and the final needed gear weight in kilograms (as outputted by the converter). Thanks! I really appreciate the help.
