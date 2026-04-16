Listen to me! The bureaucrats at the community center have completely botched our vintage clothing donation drive records! It's an absolute joke! I spend my free time volunteering, trying to keep things organized, and this is the garbage I have to deal with?! They threw everything into a messy JSON file (`donations_log.json`). And the appraisal prices? Buried in some local SQLite database (`vintage_prices.db`) because someone thought they were a tech genius.

I am specifically looking for the vintage French military garments—don't ask why, it's my own damn business and I appreciate the craftsmanship. 

Here is what you are going to do, and I expect it done flawlessly:
1. Dig through that `donations_log.json` and find every single item that mentions "French military" in its description. I don't care about capitalization, just find them!
2. Cross-reference their exact descriptions with the `catalog` table in the database to find the `price`. Note: you'll need to clean up the extra spaces those idiots left in the JSON descriptions and make sure they match the lowercase names in the database.
3. Put the results in a CSV file named `appraised_french_items.csv` with exactly these columns: `Item_ID`, `Name`, `Condition`, `Value`. 
4. Give me the sum of their values in a plain text file named `total_value.txt`.

Do it fast and do it right, I have zero patience for incompetence!
