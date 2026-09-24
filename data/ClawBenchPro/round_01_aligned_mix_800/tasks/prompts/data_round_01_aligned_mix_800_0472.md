Hey... I really need your help. I'm building a DIY plastic-body go-kart for my kids, but my wife is furious because she thinks I blew our $200 limit. 

I promised her I was tracking expenses, but honestly, my record-keeping is an absolute wasteland. I just dumped my entire 2023 financial export and my garage inventory master system into this workspace. There are hundreds of files scattered everywhere, and I have a headache just looking at it.

Here is the situation:
1. My transactions are scattered across the `financial_exports` directory, broken down by month. Some are in JSON format, some are in CSV. It contains every grocery run, bill, and random purchase I made this year. I *usually* tagged the kart stuff with something containing the word **"kart"** (like "kart-project", "diy-kart", "kids-kart", etc.) either in the JSON `project` field or the CSV `Category` column. You'll need to dig through all of them and find anything with "kart" (case-insensitive) in those fields.
2. I work shifts operating machinery at a plastics plant, so I brought home a lot of scrap from the factory floor for the bodywork. It was totally free! In the `inventory_master` directory, there is a config file for every single part number (`item_code` / `Part_Number`) listed in my transactions. If a part's `Origin` in its config file is listed as **"Factory_Scrap"** or **"Plastics_Plant"**, YOU MUST EXCLUDE IT from the cost tally. Even if the transaction lists a nominal dollar value, I didn't actually pay for it.
3. Ignore anything that was returned. If a JSON transaction's `status` is **"returned"**, or a CSV transaction's `Is_Refunded` column is **"Yes"**, drop it.

Please, write a script to sift through this nightmare, cross-reference the parts, and tally up *only* the actual out-of-pocket money I spent on valid kart parts. 

Put your final answer in a clean file at `finished_plan/budget_report.txt`. I just need the final calculated total cost, and you MUST explicitly include either the exact phrase **"UNDER BUDGET"** or **"BUSTED IT"** in the report so I know whether I need to apologize to my wife.
