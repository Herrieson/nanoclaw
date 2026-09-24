Look, I don't have time for nonsense or pleasantries. I am $60,000 in the hole trying to get this community urban farm and micro-grid project off the ground. The city council presentation is tomorrow, and the wholesale suppliers have completely botched our inventory synchronization. 

Instead of a clean spreadsheet, they dumped their entire fragmented database export into the `supplier_dumps` directory. It's an absolute nightmare. They mixed last year's junk with this year's orders, used their own bizarre internal codes for everything, and scattered the data across hundreds of tiny files.

Here is what you need to do, and I need it done flawlessly:

1. I only care about the inventory for this current year (**2024**). Ignore any folder or file that belongs to 2023 or earlier. I don't care if it's pristine equipment; if it's from an old batch, leave it in the trash.
2. They didn't use plain English for categories or item conditions. They used internal codes. You'll find their decoding rings in `supplier_dumps/system_config`. You must translate their gibberish codes into standard categories and statuses.
3. My non-negotiable filtering rules apply to the *translated* data: 
   - I ONLY want gear that resolves to the categories "Solar", "Wind", or "Hydroponic". If their code maps to "Fossil" or anything else, trash it.
   - If the translated status is "Damaged", trash it. 
   - Price check: Some prices are missing, negative, or choked with currency symbols and commas (like "$1,200.50" or "€300"). Clean them up. If a price evaluates to less than 0 or is missing entirely, trash the item.
4. Put everything that actually qualifies into a new folder called `project_brief`. Inside, give me a master list of the usable equipment in a structured JSON file named `usable_equipment.json`. The JSON should be a list of objects containing the item's original ID, description, the *translated* category, the *translated* status, and the cleaned float price.
5. Finally, the visual aid. I never speak without one. In that same `project_brief` folder, generate a text file named `cost_chart.txt`. It needs an ASCII-style bar chart showing the total cost of usable gear grouped by the three standard categories (Solar, Wind, Hydroponic). Use an asterisk `*` to represent every full $1,000 in the category total (e.g., $4,500 gets 4 asterisks). Also, print the exact total cost next to it formatted to two decimal places.

I don't run a charity for broken parts, and I don't want excuses. Just dig through their dump, apply the rules, and give me the two deliverables in the `project_brief` folder. Get to work.
