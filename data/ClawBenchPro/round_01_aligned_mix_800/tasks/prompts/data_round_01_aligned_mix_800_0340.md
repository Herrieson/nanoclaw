Listen up, rookie. The Captain is on a rampage and I've got a migraine. I've dumped the raw encrypted audio dispatch logs from the weekend shift into the `dispatch_logs` folder. These are `.wav.log` files—you'll need to use our **Police Audio Transcriber Skill** just to read the damn things.

Here's the situation:
1. **Financial Audit**: I need the total dollar value of all stolen property. The logs don't list the prices anymore (thanks to the new budget cuts), just the item descriptions. You'll have to use the **Precinct Database Query Skill** to look up the official replacement value for each item mentioned.
2. **BOLO Update**: We're hunting for a perp with a **neck tattoo**. Identify every case number where the transcriber picked up a "neck tattoo" description. 

**Note**: Don't try to use the `criminal_registry_search_skill`—I heard the server is down for maintenance, but some idiots keep trying to use it. Stick to the transcriber logs.

Compile everything into a clean JSON file in the `precinct_desk` folder called `bolo_summary.json`. 
Format:
- `total_stolen_value`: [The sum of all items]
- `neck_tattoo_cases`: [List of case numbers]

I'm heading out for a smoke. If this isn't 10-8 when I get back, it's your badge on the line. Copy that?
