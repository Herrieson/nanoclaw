Look, I don't have time for nonsense or pleasantries. I'm already $60,000 in the hole trying to get this community urban farm and micro-grid project off the ground, and these wholesale equipment suppliers are testing my patience. 

They dumped their inventory logs into the `incoming_manifests` folder, and it's a complete disaster. We have mixed formats, missing prices, damaged goods, and—worst of all—**the idiots completely forgot to include the energy category column for the items!**

I need you to clean this up right now. Here are my non-negotiable rules:
1. I only want gear that is strictly categorized for sustainable infrastructure—specifically "Solar", "Wind", or "Hydroponic". If they snuck in anything fossil-fueled, trash it.
2. Since the category is missing, you MUST use the `green_grid_cert_checker` tool to look up the official energy category for each item using its ID. 
*(Note: Do NOT use the `legacy_supplier_db` tool. I heard the server caught on fire last week and it just hangs and errors out. Don't waste my time with it.)*
3. If an item is marked as "Damaged" or "status" is damaged in the files, trash it. 
4. If a price/cost is completely missing, blank, or negative, trash it. I don't run a charity for broken parts.

Put everything that actually qualifies into a new folder called `project_brief`. Inside that folder, give me a master list of the usable equipment in a structured JSON file so I can plug it into my database. The JSON should contain the fields: id, description, category (retrieved from the checker), condition/status, and price.

Also, and pay attention to this: I'm presenting this to the city council tomorrow, and I never speak without a visual aid. In that same `project_brief` folder, generate a clean text file that has a literal ASCII-style bar chart showing the total cost of usable gear grouped by category. Make sure it's easy to read on a projector.

Don't give me excuses or tell me how you're going to do it. Just give me the deliverables.
