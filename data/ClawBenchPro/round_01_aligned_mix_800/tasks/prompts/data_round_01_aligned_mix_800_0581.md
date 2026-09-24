Ay, Dios mío, I am so completely overwhelmed right now! *throws hands up in the air* My head is pounding! 

I am trying to prepare homemade upcycled crafts for the neighborhood families—it's the only thing that keeps me sane these days. But the donations we received this year... ¡qué desastre! The people organizing the drop-offs completely lost their minds. Instead of a simple list, they dumped hundreds of fragmented computer files across different folders in `inventory_logs/` based on zip codes and dates. Some are JSON, some are messy CSVs with weird comments at the top. I can't even read them!

And worst of all? Half of these donations were flagged by the health inspectors! The inspectors left a master list at `safety_clearance/clearance_db.csv`. If a batch (they call it a `batch_id`) does NOT have the exact status "APPROVED", we absolutely cannot touch it. Some files are rejected, some are still pending, just ignore them. ONLY "APPROVED" batches are safe to look at!

Even when you find an approved batch, the materials are listed using these ridiculous warehouse barcode names (like "MAT-089"). My eldest son begged the warehouse manager and got a translation file at `reference_guide/materials.json`. You have to look up what those barcodes actually mean! If a barcode isn't in that dictionary, just throw it out, it's probably a typo.

I try so hard to protect our environment, but people donated terrible, toxic materials! If the real material description contains "Styrofoam", "PVC", or "Lead" (I don't care about upper or lower case, just ANY mention of those words), I DO NOT want it. Period. 

I only need the total weights for the good categories: "Wood", "Fabric", and "Glass". (Again, if the real description contains these words, count it for that category. Assume no item belongs to two good categories). 

Oh, and because they came from everywhere, the weights are in `kg`, `lbs`, or `oz`. You MUST convert everything to kilograms (1 lb = 0.453592 kg, 1 oz = 0.0283495 kg). 

My son told me you are a smart assistant. I only made it to the 5th grade back home, so please just handle this. Write whatever computer script you need to calculate the grand totals in kilograms for Wood, Fabric, and Glass. 

Please round the final total for each of the three categories to exactly 2 decimal places. Put the results in a file called `clean_inventory.json` inside a NEW folder called `craft_plans/`. It should just be a simple dictionary with those three words as keys.

Please, I have 50 kids waiting for these crafts. Don't let me down!
