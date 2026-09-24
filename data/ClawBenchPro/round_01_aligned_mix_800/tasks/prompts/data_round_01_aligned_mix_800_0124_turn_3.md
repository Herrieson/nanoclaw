Okay, take a deep breath. The venue map is finally here, and it's time to set up. I really prefer things to be orderly and traditional.

The layout is in `venues/map.json`. It outlines the different display zones we have, their square footage capacity, and their sunlight conditions. 

I need you to take our final, updated purchasing list from your records and assign every single item to a zone in the venue. But there are strict physical rules:
1. An item's `sunlight` or `maintenance` need (like full_sun, partial_shade, etc. depending on the catalog's naming) must exactly match the zone's sunlight condition.
2. The sum of the `size_sqft` (or `area_sqft`) of all items placed in a single zone cannot exceed 80% of that zone's total capacity (we need walking room for the guests).
3. We cannot mix historical artifacts and live plants in the exact same zone. You'll need to figure out which is which based on the catalogs (plants usually have sunlight/maintenance needs, artifacts might be categorized differently or have 'none' for sunlight).

Please create a final document named `Floor_Plan_Manifest.txt` in the root directory. It should list each zone, and underneath it, the names and IDs of the items assigned there, along with the total square footage used versus the zone's capacity limit. Please ensure everything is perfectly calculated; I can't handle any more surprises on opening day!
