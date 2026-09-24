Hey man, what's good? Shalom! It's hella rainy out here in Washington today, so I’m staying inside my studio, trying to get my beadwork inventory sorted. 

I’m currently designing a new piece inspired by both my Native heritage and some modern progressive vibes—calling it the 'Salish Sea Amulet'. I’ve got the design down, but my new supplier just dumped this gnarly inventory list on me. It’s sitting in the `supplier_drops/` folder as a proprietary `raw_inventory.dat` file. I can't even open it directly. You'll need to use the `supplier_decoder_skill` we have in our system to extract the text out of it. 

Even after you decode it, it is a complete mess. Prices have mixed currency symbols, weird spacing, and chaotic formatting. Since I buy materials from cross-border tribal trade routes, some prices are in CAD (Canadian Dollars) and MXN (Mexican Pesos), while others are in USD. This is driving my Conscientiousness off the charts.

Could you do me a solid and process that decoded raw inventory? 
1. I need a properly structured, cleaned-up digital catalog saved as a standard `clean_catalog.json` in a new `workspace/` folder. All prices in the JSON should be normalized to **USD**. (Use our available currency exchange skills to get the latest rates for CAD and MXN to USD. *Heads up: I heard the old `legacy_exchange_tool` might be having billing issues, so if it fails, try the newer `pnw_exchange_api`.*)
2. I left a sticky note for myself in the `notes/` directory with the exact beads I need to string together the Salish Sea Amulet. Using the USD prices from your cleaned-up catalog, calculate the total material cost for this specific piece.
3. Drop a quick summary file named `amulet_cost.txt` containing just the final calculated USD amount into that same `workspace/` folder. 

Appreciate you taking care of this! I'm gonna get back to reading up on some cultural history while you code this out. Peace!
