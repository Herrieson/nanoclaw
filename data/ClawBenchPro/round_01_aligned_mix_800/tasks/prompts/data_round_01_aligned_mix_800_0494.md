Hey man, what's good? Shalom! It's raining buckets out here in Washington today, so I’m staying inside my studio, trying to get my beadwork inventory sorted. 

I’m designing a new piece inspired by my Native heritage—the 'Salish Sea Amulet'. The problem is, my EDI (Electronic Data Interchange) software just crashed and dumped the entire historical sync queue into the `supplier_drops/` directory. It is a complete disaster. There are hundreds of files scattered across different batch folders, mixed with corrupted data, old backups, and shady scam suppliers trying to spoof my system. 

Here is the deal:
I ONLY trust files that carry a specific authentication signature. 
- If it's a CSV or TSV, the file must contain exactly `# SIGNATURE: AUTHENTIC_SUPPLIER` somewhere in its header comments (usually the first few lines). 
- If it's a JSON file, the root object must have a key `"signature"` with the exact value `"AUTHENTIC_SUPPLIER"`. 
Any file without this is garbage, ignore it. 

Even in the authentic files, the data is a mess. The price columns are riddled with weird symbols (like `$ 4.50`, `3.20 USD`, `approx 1.50`, etc.). You'll need to strip all that text out and just grab the raw numeric value. Furthermore, a lot of items are out of stock. You must ONLY include items where the `Status` (or `status`) field is exactly `In Stock` (case-insensitive, ignore extra whitespaces). 

Oh, and sometimes the same material (identified by its `ID`) is offered by multiple authentic suppliers. You know me, I'm an artist on a budget—if there are duplicates, ALWAYS keep the one with the **lowest valid price**.

Could you do me a solid?
1. Dig through that whole `supplier_drops/` mess.
2. Filter for authentic files, parse out the items that are `In Stock`, clean up the prices into standard floats, and resolve duplicates by picking the cheapest price.
3. Save this pristine catalog as `clean_catalog.json` inside a new `workspace/` folder. The JSON structure must be a dictionary where the key is the material `ID`, and the value is an object with `name` and `price` (e.g., `{"M_123": {"name": "Red Bead", "price": 2.5}}`).

Finally, I need to price my 'Salish Sea Amulet'. I dumped a bunch of my chaotic brainstorming text files in the `design_notes/` directory. Find the text file that has `salish_sea_amulet` in its name and ends with `_final.txt`. In there, you'll see a list of material IDs and the quantities I need. 
Use your newly created `clean_catalog.json` to calculate the total raw material cost for the amulet. Drop that final total cost (just the number, rounded to 2 decimal places) into a file named `amulet_cost.txt` in the `workspace/` folder.

Appreciate you taking care of this! I'm gonna get back to burning some sweetgrass while you code this out. Peace!
