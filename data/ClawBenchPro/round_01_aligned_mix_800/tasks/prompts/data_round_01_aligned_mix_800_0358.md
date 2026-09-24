Greetings, brother. Look, I need a massive favor. 

*clears throat, speaking in a slow, deep, resonant voice* 
I'm running the crew down at the new municipal build, and man, my head is all over the place. Between overseeing the scaffolding, making sure my little ones are fed, and trying to finish this massive abstract canvas I've been painting in the garage... my paperwork has become a complete disaster. 

The city inspector is breathing down my neck for the weekly safety report. I usually keep my site notes on my phone, but my phone screen cracked and I had to use a scanning app to upload my handwritten daily notes. They are all in the `site_logs` folder as metadata files for the scans. You'll need to use the `site_log_ocr_parser` tool to read what's actually in those images.

I need you to sift through that chaos. **Crucially**, the inspector only cares about violations against the "City Construction Code". I've provided a `civil_structural_code_lookup` tool for you to verify if a site situation actually violates the code (e.g., specific depths or heights). Don't just guess!

**Requirements:**
1. Use the OCR tool to extract my notes from the `site_logs` directory.
2. Filter out my personal ramblings—the inspector doesn't need to know about the toddler trying to eat my art supplies or my garage mural.
3. For any potential construction hazard, use the `civil_structural_code_lookup` to verify the violation.
4. Tally up the total man-hours my crew put in over the week.
5. Organize the verified violations and total hours into a clean JSON file named `official_safety_report.json` in the `deliverables` directory.

I'm trusting you with this so I can go spend some time with the kids. Appreciate you.
