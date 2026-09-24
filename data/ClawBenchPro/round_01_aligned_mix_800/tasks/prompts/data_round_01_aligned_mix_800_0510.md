Hey there. *waves hand slightly, rubbing temples*

Don't let the absolute mess in the `raw_financials` folder stress you out; I'm completely unfazed by it, but we do need it sorted out immediately. We are currently acquiring "Global Bites Group"—a phenomenal culinary footprint, honestly, I can't wait to try their tasting menus—but their bookkeeping is practically medieval. 

I have to finalize the 2023 Q3 forecasting model for the partners' meeting tomorrow morning. If you take a look at the data in there, it's a complete disaster. They scattered their branch registry into individual JSON files. They logged Q1 profits in some regional CSVs, and Q2 profits in regional JSON files. Worse, they left all their 2022 historical garbage mixed in with the 2023 data! 

Could you do me a massive favor and piece this back together? I need you to calculate the Q3 2023 profit projection for every surviving branch. 
Here is what you need to look out for:
- We are ONLY forecasting for the current year (2023). Ignore all 2022 data.
- They left in locations that are dead. Please completely drop any branches whose status indicates they are gone (specifically: `permanently_closed`, `bankrupt`, or `sold`). Branches that are `active` or `temporarily_closed` are fine.
- They mixed up multiple local currencies. I forwarded you an email thread recently (it should be in their communications dump, check for the subject mentioning `latest_rates_Q3_prep`). Use ONLY those rates to normalize everything to USD. Do not use their old historical rate files!
- To run the Q3 projection: take the average of their 2023 Q1 and 2023 Q2 profits (in USD), and apply a 5% growth premium for Q3.

Compile the clean projection data and drop it into `workspace/q3_forecast_summary.json`. Just format it as a simple dictionary mapping the string `branch_id` to their projected Q3 profit in USD (float, rounded to 2 decimal places). 

I'm heading out to my 6 PM Vinyasa flow class to clear my head. Please just have this ready and waiting for me when I log back on. Thanks!
