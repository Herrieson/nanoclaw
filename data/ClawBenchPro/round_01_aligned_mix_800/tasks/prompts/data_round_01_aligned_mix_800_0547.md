Oh my Lord... *hums a nervous, off-key church hymn* ... I am at my wit's end today! I bought this cheap OCR scanner to digitize all my old recipe cards for the church bake sale, and it just made a colossal mess! It dumped hundreds of files into the `recipes` folder and a whole chaotic maze of subfolders. I can't even find my own Aunt Sally's pie recipe anymore!

Look, I need your help to figure out my grocery list, but my budget is tighter than my corset on Sunday. Here is what you need to know to sift through this digital landfill:

1. The scanner created a bunch of weird backup files. Please ONLY look at the `.txt` files in the `recipes` folder and all its subfolders. Ignore anything with another extension.
2. Some of the text files are just rambling stories about my grandma or they completely missed scanning the ingredients. If a `.txt` file does NOT contain a line that says exactly `Ingredients:` or `[Ingredients]` (case-insensitive), just throw it out. 
3. Right below that header, the ingredients are listed one per line, formatted exactly like `IngredientName: Quantity` (for example, `Flour: 2` or `Brown Sugar: 1.5`). The ingredients list stops as soon as there is a blank line or a new section like `Instructions:`.
4. *Heavy sigh* During my wild experimental phase, I wrote down recipes using `saffron`, `caviar`, or `truffles`. If you see any of those three words ANYWHERE in the ingredients list of a recipe (for example, "White Truffles" or "Iranian Saffron"—no matter how they are capitalized), IGNORE that entire recipe! I cannot afford those!

For the sensible recipes that actually survive all these rules, I need to make EXACTLY 3 batches of each for the bake sale. 

Could you multiply all the ingredient amounts from the valid recipes by 3, and total them all up? If two different recipes use "Flour", add them together. Make sure to convert all ingredient names to lowercase (so "Flour" and "fLoUr" become "flour") so the final list is neat. 

Put the final tally in a file called `list.json` inside a brand new folder named `grocery`. I need it as a simple JSON map (e.g., `{"flour": 12.0, "eggs": 9.0}`) so I know exactly how much of everything to buy and don't panic at the cashier stand. Bless your heart!
