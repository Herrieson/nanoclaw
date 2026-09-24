Oh, for heaven's sake! If I have to look at another disorganized pile of paperwork from this incompetent front office, I might just lose my mind! 

Look, we are taking my 6th graders on an overnight nature hike next week—May 15, 2024 (2024-05-15), to be exact. It's what I live for. But the administration just dumped the entire school's multi-year parent volunteer database and every single scrambled expense receipt into my lap. I have my own kids to pick up and my garden isn't going to weed itself today!

Here is what I need you to do, and use a script if you have to, because I am NOT doing this by hand:

First, figure out who is ACTUALLY qualified to chaperone. The data is a nightmare:
1. The applicants' basic files are scattered in `records/volunteers/applicants/` as endless JSON files.
2. The background checks are dumped in one massive `records/volunteers/bg_checks.csv`. I absolutely refuse to take anyone whose `status` isn't strictly `Pass` OR whose `valid_until` date is on or before our trip date (2024-05-15). If it's expired or expires on the day of the trip, they stay home!
3. And the first aid certificates? They scanned them into a chaotic mess of text files under `records/volunteers/first_aid_certs/`. You'll have to dig through those files to find which ones belong to which applicant ID, and ensure the text explicitly says `Status: Active`.

Only give me the NAMES of the volunteers who pass ALL THREE of these checks. 

Second, the budget. Someone went crazy at the sporting goods store, and the receipts are tossed into monthly folders under `supplies/receipts/`. 
I only care about our specific trip! Ignore all the other school events. Our `event_code` is exactly `6TH-GRADE-HIKE-24`. Furthermore, I only want to calculate the receipts where the `status` is `Paid` (ignore the Voided, Pending, or Refunded ones). Figure out the total cost by summing up the `(cost * quantity)` of every item in those valid receipts.

Generate a clean JSON file named `trip_summary.json` and put it right in the `reports/` folder. I don't care what you name the fields inside it, but it MUST clearly contain a list of the approved volunteers' names and the final grand total of our specific supply costs. 

Don't give me any fluff, don't ask me for clarifications. Just write whatever code you need to sort this data nightmare out so I can finalize my lesson plans. Can you handle that?
