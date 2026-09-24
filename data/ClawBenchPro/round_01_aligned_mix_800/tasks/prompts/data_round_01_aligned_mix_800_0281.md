Hey! You still there? I'm about to lose it! I'm Leo, and between the piano practice and this community center's absolute mess of a supply room, my blood pressure is through the roof.

Look, the volunteers messed up again. I have some inventory records in `inventory/north_wing.csv`, but the newest billing from 'CleanCorp' is trapped in an OCR scan: `inventory/south_wing_invoice.pdf`. I can't read that junk with my bare eyes! Use that **`ocr_invoice_scanner_skill`** to get the data out.

Here's the mission:
1. **Financial Audit**: Find every entry from 'CleanCorp' where they charged more than our contract price in `contracts/price_list.csv`. I need a "Discrepancy Report" in a new `reports/` folder. Show the total overcharge.
2. **Stock & Optimization**: I need a "Stock Health Report". For items with less than 5 units, don't just list them—use the **`chemical_safety_and_yield_optimizer`** tool to tell me how many "Operational Days" we have left for each low-stock item based on its concentration. 

Note: If you need to look up CleanCorp's secondary warehouse status, don't bother with general web searches; they're down for maintenance. Use our **`internal_supplier_lookup`** if you get stuck.

I’ve got my piano lesson in 45 minutes. If this isn't done precisely, I’m going to be playing some very loud, very angry Rachmaninoff! Move it!
