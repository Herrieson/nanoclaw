Oh my god, you're a lifesaver. *runs hands through hair frantically* I am officially 15 minutes late to pick up Chloe from middle school, and my preliminary grant report for the rare meteorite research is due at midnight! If I don't get this submitted, the lab loses its funding!

The undergraduate interns this semester are an absolute disaster. I asked them to catalog the spectrometer data, and instead, they created a massive digital landfill. They dumped hundreds of files into the `raw_spectrometer_dumps/` directory, organized by whoever was on shift. 

Here is what you need to fix for me before I lose my mind:

1. **The Inventory Nightmare**: They tested *everything* in the lab, including the decorative paperweights. I only need data for my authenticated collection. The official museum database export is located at `museum_exports/inventory_2023.csv`. You must ONLY process artifacts where the `Status` is strictly marked as `VERIFIED`. Ignore anything 'PENDING' or 'REJECTED'.

2. **The Broken Equipment**: I have told Chad a million times that the 'Beta' spectrometer has a cracked focusing lens! Any data coming from the `Beta` machine is completely invalid. You must filter out any readings where the machine/device/spectrometer is listed as `Beta`. Only trust `Alpha` or `Gamma`.

3. **The Schema Chaos**: They couldn't even agree on a file format! 
   - **Sarah** used CSVs, but she named her columns things like `weight_g` and `size_cm3`.
   - **Kevin** used flat JSON arrays, but abbreviated everything to `m` for mass and `v` for volume, and `item` for the ID.
   - **Chad** used JSONs too, but he nested his actual readings inside a `data` array and put the machine info in a `metadata` block. 
   - They also forgot to calibrate the scales. If you find any readings where the mass or volume is negative, zero, or just completely missing/null, throw that specific reading out immediately! Oh, and watch out—Kevin mentioned his laptop crashed during some exports, so there might be corrupted, unreadable files in there. Just skip the corrupted ones!

I need you to calculate the average density (mass divided by volume) for each of my `VERIFIED` artifacts based *only* on the valid readings. 

Please, process this mess and put a clean summary file into a new directory called `grant_submission`. I don't care what the file format is—JSON, CSV, whatever—just make sure the artifact IDs are clearly mapped to their calculated average densities so I can blindly copy-paste it into my manuscript tonight. 

I'm running out the door! I owe you my life!
