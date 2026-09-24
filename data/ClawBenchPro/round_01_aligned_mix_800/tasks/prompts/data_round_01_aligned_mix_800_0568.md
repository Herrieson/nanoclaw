Look, I don't have the energy to sugarcoat this—my toddler has been screaming for an hour, I'm working on three hours of sleep, and my store manager just dropped a massive headache on my lap. 

I work customer service at this retail chain, and I've been pushing them for months to take our "Cultural Diversity and Accessibility" initiative seriously. IT finally collected the data, but whoever exported it from our dinosaur-era POS system completely botched it. 

They dumped everything into a `raw_feedback` folder, and it's a complete disaster. It's scattered across dozens of subfolders. Some of the `.dat` files are readable JSON arrays, some are JSON lines, and others are just lines of absolute gibberish because the system encodes them in Base64 for absolutely no logical reason. And some files even have corrupted garbage lines in them! 

Here is what I need you to do:
1. Dig through the entire `raw_feedback/logs` directory. Figure out how to parse those `.dat` files, whatever format they are in.
2. Filter for actual customer feedback. The POS system logs everything, so you'll see system errors complaining about "accessibility APIs" or employee reviews. I ONLY want entries where the `type` is exactly `"feedback"` (anything else is useless IT garbage).
3. Within those customer feedback entries, find every single one that explicitly mentions the words "diversity" or "accessibility" in the `comment` (case doesn't matter, people type how they type).
4. The logs only give you a user ID (`u_id`). You have to match that to the customer's real name. They left multiple exports in the `raw_feedback/registry` folder. Please, for the love of god, only use `registry_FINAL_2023.csv` to look up their names. The older backups are full of broken data and will give you the wrong names.

Once you have all the matching customer feedback with their real names, create a new `deliverables` directory and save a clean `report.json` file in it. 
The JSON must look exactly like this:
{
  "total": <number_of_matches>,
  "results": [
    {
      "name": "<Customer Name>",
      "comment": "<exact feedback text>"
    }
  ]
}

Do whatever you have to do in Python or bash to parse it, just get it done quickly so I can email this report to corporate and finally go comfort my kid.
