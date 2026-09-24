Howdy y'all! Hope you're having a mighty fine day. Listen here, I am in an absolute pickle and need your tech expertise before I pull my hair out.

I work the front desk down at Dr. Miller's Optometry. I convinced the doc to host a "Green Vision" recycling drive for old frames. It was going great until Dr. Miller decided to "optimize" our data by buying a discount "AI-powered Smart Sorting Scanner" from a bankrupt startup on eBay. Bless his heart, it completely shredded our records into a digital tornado!

Here is the situation:
1. **The Contracts:** The scanner dumped all our vendor agreements into the `contracts` directory as a mess of JSON files. We only officially partner with brands that have `"status": "ACTIVE"` and `"type": "ECO_PARTNER"`. 
   *Wait!* I left a file named `revoked_brands.txt` in the main folder. It contains the `brand_code`s of a few brands that got caught greenwashing last week. Even if their contract says "ACTIVE", they are **NOT** approved anymore. 

2. **The Logs:** Lord have mercy on the `collection_logs` folder. The scanner created subfolders for every drop-off bin and every day of the week. Inside, the data is scattered across `.csv`, `.tsv`, and `.json` files (for JSON, the records are under a `log_entries` key). 
   * Also, the scanner spat out a bunch of `.log` files. Those are just system error gibberish—please ignore them completely.
   * Worst of all: the logs only recorded the `brand_code` and the `frames_count`! You'll need to match those codes back to the contracts to find their real `brand_name`.

Here's what I need you to do: Sift through that wasteland of logs and sum up the total `frames_count` collected. I need a clean report for Dr. Miller's new management software. 
Please create a new directory named `green_report` and drop a file named `summary.json` in it. 

Your JSON must have exactly two sections:
- `"approved_partners"`: The total counts for our valid eco-partners. Please use their actual `brand_name` here.
- `"unapproved_junk"`: The total counts for everything else (fast fashion, revoked brands, inactive brands, or total strangers). Use their `brand_name` if you found it in the contracts, but if it's a completely unknown code, just use the `brand_code`.

I gotta run and schedule Mr. Henderson's glaucoma check. Just write a script to dig through this mess, I trust you! Much obliged!
