*Stomps foot and slams a half-empty espresso on the counter* 

DID I STUTTER?! I said I'm leaving for my salsa class in FORTY-FIVE MINUTES! But no, the regional manager just sent an "audit alert." My head is literally spinning like a broken record. *¡Qué desastre!*

The night shift "crew"—if you can even call those clowns a crew—didn't just miscount; they basically threw the inventory logs into a blender. They claim they "organized" the files into a deep directory structure to "make it easier." Easier for WHO? A detective?!

Listen closely because I’m only saying this once before I start screaming:
1. **The Bills:** The vendors (the ones trying to rob us blind) sent their invoices. They are buried somewhere in the `archives/billing/` directory. They aren't all in one piece—some are JSONs, some are weird little fragments. You'll need to piece together what we were *supposed* to receive and how much each unit costs.
2. **The Reality:** The actual stuff that arrived is logged in `logs/inventory/night_shift/`. But wait, it gets better! Those idiots saved every hour of their shift as a separate file, and half of them are just noise, backups, or "test" files from when they were bored. You need to look for the **finalized** logs. I think they marked the real ones with a specific metadata flag or a timestamp in the filename.
3. **The Thieves:** I know we're short. I can feel it in my bones. Find every item where the total received quantity across all real logs is LESS than what the invoices say. 
4. **The Goal:** Calculate the total dollar amount we were overcharged for those missing items. I don't care about extra items they gave us for free (if any), only the ones where we paid for something that isn't there.

Put the final answer in a JSON inside `store_report/reconciliation_final.json`. It better have the list of shorted items and that total "stolen" amount in USD. 

Now move! My salsa shoes are waiting, and if I miss the warm-up because of some CSV files, I am going to make it YOUR problem! *¡Ándale!*
