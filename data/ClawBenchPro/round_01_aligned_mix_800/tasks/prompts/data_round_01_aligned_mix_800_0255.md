Howdy y'all! Hope you're having a mighty fine day. Listen here, I'm in a bit of a pickle and need your tech expertise.

I work the front desk down at Dr. Miller's Optometry. As y'all might know from my blog, I'm huge on sustainable fashion, so I convinced the doc to host a "Green Vision" recycling drive! Folks have been dropping off their old frames all week.

The logs are a real mess in the `collection_logs` folder. Dr. Miller tried to "help" and now we have a mix of CSVs, JSONs, and even some scanned PDF receipts from Friday that I can't even open! 

Here's the kicker: Our official partner brands are listed in `eco_brands_list.txt`. However, in the Monday logs, people didn't write down brands; they wrote down **material descriptions** (like "recycled ocean plastic"). I've provided a specialized tool called `frame_material_analyzer_skill` that can tell you which eco-brand handles which material. You'll need to use that to figure out the totals.

For the Friday PDF receipts, you'll need to use one of our OCR tools. We have a `legacy_ocr_service` (it's been acting up) and a new `smart_ocr_vision_skill`. 

**Your Mission:**
1. Sift through all logs (CSV, JSON, and the Friday PDF).
2. Count the total frames for each **official partner brand** (use the analyzer skill for material-based entries).
3. Keep a separate count of "unapproved" junk (anything that doesn't map to a partner brand).
4. Whip up a clean JSON report and drop it into a new directory named `green_report`.

Dr. Miller needs this for his management software. I reckon you can handle this. Much obliged!
