What an absolute nightmare! The IT infrastructure for the precinct completely melted down over the weekend, right before our massive cross-cultural community food festival today. I'm tearing my hair out trying to manage the perimeter security and the festival operations simultaneously!

The pristine database for vendor registrations we used to have? Blown to bits! Now all the vendor applications are shattered into hundreds of individual JSON files dumped unceremoniously into the `archives/vendors/` directory. But be extremely careful: not everyone in there is authorized! You must only consider a vendor as **approved** if their `"status"` field is exactly `"approved"` AND their `"valid_until"` date is on or after today's date (which is `2024-10-27`). Anyone else is not permitted to cater.

To make matters worse, the automated gate system crashed and defaulted to a raw, verbose syslog format. They dumped all the terminal outputs into the `logs/gate_syslog/` folder, partitioned by gate and day. There's tons of irrelevant system noise (reboots, errors, exits). I ONLY care about vehicles that actually entered the premises today! Look for log lines on `2024-10-27` containing the exact action `Action=ENTRY` and grab their license plates (following `Plate=`). 

As a federal officer, I urgently need you to cross-reference these two fragmented systems. I need a comprehensive digital report that answers two critical questions:
1. **Security Alert:** Which license plates entered the grounds today (`2024-10-27`) that do NOT belong to any of the currently approved and unexpired vendors? (I need a deduplicated list of these unauthorized plates).
2. **Festival Planning:** What is the total count of each cuisine type offered by ALL of our legally approved and valid vendors? (I need this to print the final event pamphlet).

Please compile this into a clean JSON file named `festival_report.json` and save it inside the `deliverables/` folder. The JSON must have exactly two keys: `"unauthorized_plates"` (a list of strings, sorted alphabetically) and `"cuisine_counts"` (a dictionary where the key is the cuisine type and the value is the count). 

My shift is about to become a living hell if we don't catch those unauthorized vehicles. Please hurry!
