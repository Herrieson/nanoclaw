Hello. I need you to look into a script we use for processing aircraft component drafts. I'm taking the wife and kids camping this weekend up in the mountains, so I really want to get this off my desk and finalized before I log off. 

In my workspace, there is a folder called `draft_specs` containing JSON files for various new and legacy aircraft parts. I wrote a Python script called `process_drafts.py` that is supposed to read all these files and generate a `bom.csv` (Bill of Materials) containing the 'Part ID', 'Material', and 'Weight'. However, it crashes on some of the older files from our legacy system because they are poorly formatted. 

Please fix the script so it handles missing 'weight' or 'material' fields gracefully. If 'weight' is missing, default it to 0. If 'material' is missing, default it to 'Unknown'. Make sure it successfully outputs the complete `bom.csv`. 

Additionally, because of a recent supply chain issue, I need a separate text file named `titanium_parts.txt` listing just the Part IDs of any component where the material is Titanium. The legacy system sometimes capitalized it weirdly, so make sure your check is case-insensitive. Just put one Part ID per line in that file.

Both `bom.csv` and `titanium_parts.txt` should be saved directly in my main workspace directory. I appreciate the help.
