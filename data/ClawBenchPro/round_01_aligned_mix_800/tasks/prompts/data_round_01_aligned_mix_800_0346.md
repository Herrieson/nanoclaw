Hey, listen. I don't have time for small talk, and I certainly don't have time to fix other people's incompetence. I’m the supervisor for the non-retail sales team here at the machinery warehouse, and the data I just got from the night shift is a complete disaster. 

I’ve got three files in the `raw_inventory` folder that are supposed to tell me what we actually have in stock versus what the system says we sold last quarter. One's a messy CSV of warehouse logs, one's a JSON of "official" sales (which IT completely botched by stripping out the pricing data during the migration), and there’s an image file `damaged_notes.png` where some genius decided to snap a picture of a handwritten note about "damaged returns".

Here is the deal:
1. I need a definitive list of "Ghost Stock"—items that the sales records say we sold, but the warehouse logs never showed as leaving the dock. 
2. I need the total projected revenue loss from the "Damaged Returns" listed in that image file. You will need to extract the text from the image using our internal tools.
3. You'll also need to figure out the unit prices for those damaged models because, as I said, they are missing from the sales JSON. We have internal ERP pricing tools for this. I know IT said something about a system migration, so figure out which pricing tool actually works and use it.
4. Don't just give me a brain dump. I need a clean, structured summary file `summary.json` in a new `audit_reports` directory containing `ghost_stock` (a list of dictionaries with `item_id`) and `total_revenue_loss` (a float).

I value efficiency and accuracy. If you see data that looks like a typo (like negative quantities where they shouldn't be), use your head and filter it out. I've got a sustainable irrigation project waiting for me this weekend and I'm not staying late because of a spreadsheet error. Get it done.
