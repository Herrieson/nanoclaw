*(Adjusts her glasses and sighs deeply, her posture rigidly straight, glaring at you across a desk littered with disorganized papers)*

Listen to me very carefully. I do not have the patience for another administrative disaster today. I supervise the food preparation for the State Government's annual "Literature & Community Activism" banquet. Thanks to the IT department's "seamless migration," our financial records and attendee databases have been blown to pieces, and I absolutely refuse to be audited because someone couldn't do simple bookkeeping.

First, look in the `financials/` directory. They didn't just dump the receipts; they scattered thousands of raw financial logs across multiple quarters and weeks. Some are JSON files, some are plain text. It’s an absolute landfill. I only care about the expenses that are officially verified. For the text files, you'll know they are valid because they have exactly `STATUS: VERIFIED` at the very top. For the JSON files, the `status` key will be exactly `VERIFIED`. Ignore all the pending, draft, or rejected garbage! 

Once you isolate the verified files, I need to know exactly how much we are spending on actual sustenance. Comb through their items and sum up every single expense where the item name starts explicitly with "Food" or "Beverage" (case-sensitive). Ignore the speaker fees, security, decor—my budget strictly covers dining services!

Second, the attendee data is just as infuriating. IT fragmented the master list into 50 separate batch CSVs in the `registrations/` folder. I need you to comb through every single batch. Find the attendees whose ticket type is **EXACTLY** `VIP` (do not include "V.I.P", "vip", "VIP Guest", or any other nonsense variations the interns typed). 

Every VIP has complex dietary requirements, yet some lazy staff member left the `diet_notes` for several VIPs completely blank (or just full of empty spaces), or marked them as "none" or "n/a" (in various random capitalizations like "None", "N/A", "none", etc.). I won't have a PR disaster when a renowned author is served something they can't eat. I need you to isolate the `full_name` of every single VIP who has one of these problematic or missing dietary values.

Use your head. Write a reliable script to parse this mess. When you have the answers, create a clean JSON file named `audit.json` directly in the `desk/` folder. I don't care what you name the two internal keys, as long as one contains the exact total float cost of the food/beverage, and the other contains the list of those problematic VIPs' names. 

Get it done. I have to go scream at the venue contractors.
