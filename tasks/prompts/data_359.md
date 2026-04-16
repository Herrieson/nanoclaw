Listen, I’m tapping my foot here waiting for this to be done. Between wrangling my toddler and processing endless insurance claims for the firm, I barely have a moment to breathe. I need you to handle a very specific project for me. 

As an avid birder, I've noticed a strange trend in our New Mexico property damage claims related to local bird species—specifically Woodpeckers and Wild Turkeys. My boss won't believe me unless I have rock-solid, verified data. 

I exported a batch of recent claim logs into the `claims` folder in the current directory. They are messy, plain text exports from our legacy system. I also created a `nm_bird_habitats.json` file that maps those two bird species to the zip codes they actually inhabit. 

I need you to go through all those claim files. Find the claims where the damage description explicitly mentions a "Woodpecker" or a "Wild Turkey" (case-insensitive, but record the species name properly in your output). Then, cross-reference the zip code on the claim with the habitat JSON. If the zip code matches the bird's known habitat, it's a verified avian claim. If it mentions the bird but the zip code is wrong, discard it—it's either a misidentification or fraud.

Generate a CSV named `avian_claims_report.csv` in the current directory with the exact columns: `ClaimID,Date,ZipCode,Amount,Species`. 
Finally, calculate the total payout amount for these verified claims and write just that number (e.g., 1234.56) into a file called `total_payout.txt`. 

Do it right, and do it fast. I appreciate hard work and precision, and I have zero tolerance for sloppy data. Let me know when it's done so I can take the kids to the park.
