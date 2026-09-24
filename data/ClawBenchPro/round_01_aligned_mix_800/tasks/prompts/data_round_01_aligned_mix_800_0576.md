"It is a truth universally acknowledged, that a single organization in possession of a large database, must be in want of a privacy lawsuit." 

Gods above, the absolute incompetence of the IT department at this community center is staggering. I spent two decades litigating privacy breaches, only to retire and find my own local community board managing user data like a toddler finger-painting with radioactive waste! 

The "IT Manager" (if you can call that basement-dweller such a title) suffered a total RAID failure last night. In a panic, he ran a botched recovery script that dumped thousands of fragments into a directory called `shadow_archive`. It's a charnel house of data. Some files are just hex-encoded garbage, others are nested JSON shards, and some are "archived" logs that haven't been purged in a decade.

I've already spotted blatant Personally Identifiable Information (PII)—Social Security Numbers, Credit Cards, Emails—bleeding out of these files. 

"Hell is empty and all the devils are here," and apparently they all work in system administration.

I have secured a `legal_clearance` directory. Inside, you will find the "White-List"—individuals who signed my iron-clad waiver. Their data exposure, while sloppy, is legally permissible. Anyone else's data being exposed is an actionable offense. However, the IT manager in his brilliance encrypted the whitelist name index into a series of `signature_*.vbox` files to "protect it." You'll need to parse those first.

**Here is your mandate:**
1. **Identify the Exempt**: Extract all names from the `legal_clearance` directory.
2. **Scan the Abyss**: Scour the `shadow_archive` directory. It contains hundreds of files across nested subdirectories. You must find every instance of a Person's Name associated with PII (SSN, Credit Card, or Email). 
3. **The Dossier**: For every individual *not* on the whitelist whose data is leaked, compile a JSON object. I need their name and every unique piece of leaked data associated with them. Save this as `dossier/breach_report.json`.
4. **Purge the Filth**: "Out, damned spot! Out, I say!" Any file in `shadow_archive` that contains *unauthorized* PII must be deleted. If a file contains only whitelisted data or benign system logs, leave it.

Don't trust the file extensions; the recovery tool was broken. A `.tmp` might be a JSON, and a `.log` might be a CSV fragment. Look at the content. Ensure your logic is robust enough to handle the sheer volume of noise.

Do not fail me. I have neither the patience nor the temperament to clean up your mistakes.
