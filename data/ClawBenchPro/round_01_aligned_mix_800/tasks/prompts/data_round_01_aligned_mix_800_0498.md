Hey... *sighs, rubbing temples* I apologize for the mess you're about to see. 

I was just trying to plan this culturally diverse dinner party using my company's corporate procurement system—since I get a massive employee discount—but our IT department just migrated the legacy database, and it is a complete wasteland. 

My boss dumped the entire vendor quote history into the `quotes` directory. It is flooded with hundreds of folders, old drafts, rejected bids, and garbled backups. I don't have the mental energy or the time to manually forecast the budget for next weekend's tasting event, so I need you to step in as my trusty junior analyst and crunch the numbers.

Here is the corporate survival guide for navigating this mess:
First, you absolutely must cross-reference everything with the master registry located at `procurement/vendor_registry.csv`. I only want to do business with vendors whose status is exactly `APPROVED`. Ignore everyone else—they are blacklisted, pending, or out of business.

For those approved vendors, dive into their specific subfolders in the `quotes` directory. You will see a lot of junk files. Ignore the drafts, the text notes, and the temporary backups. The **only** file you should read for an approved vendor is the one whose filename starts exactly with `final_quote` and ends with either `.json` or `.csv`. There is exactly one such file per approved vendor.

Next, we need to calculate the budget. Check `procurement/rules.json`. It contains the active `exchange_rates` you need to convert all current prices into USD. 
It also contains a list of `premium_tags`. If a quote item's tags (which might be an array in JSON, or a pipe-separated `|` string in CSVs) contain ANY tag that matches one of our `premium_tags`, you must apply the `premium_fee_multiplier` (also found in the rules) to its converted USD price. 

Also, my health-conscious lifestyle means I'm very picky about inflation. I need you to flag the exact `item_name` of any ingredient or wine where the raw `current_price` has spiked by strictly more than 15% compared to its `base_price` (just compare the raw numbers provided, don't worry about currency conversion for the spike check).

Put your final report in a clean JSON format named `dinner_budget.json` and drop it into the `financial_forecast` folder. Make sure your JSON has exactly two keys: `total_usd_cost` (the grand total in USD as a float) and `flagged_items` (a list of names of the spiked items). 

I'm heading to the farmer's market before they run out of heirloom tomatoes. I trust you'll have navigated this labyrinth and forecasted it perfectly by the time I get back!
