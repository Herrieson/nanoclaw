Omg I'm literally freaking out right now!!! 😭 I was trying to organize my digital book database for my campus bookstore job, and I ran this script a friend gave me to "clean" the data. It completely ruined everything! I'm already drowning in like $60,000 of student debt, and if I lose this job because I corrupted the inventory catalog, I honestly don't know what I'll do. 

Please, please help me fix it. Everything is in the `./` folder.

Here is exactly what went wrong:
1. The `scrambled_catalog.csv` file is a mess. The `Title` and `Author` columns got completely swapped with each other. Even worse, the `Year` column got converted into these weird hex strings (like `0x785` instead of normal years)!! I need you to create a `fixed_catalog.csv` in the same folder. It must have the columns in the correct order (`ID`, `Title`, `Author`, `Year`, `Genre`) and the years must be normal numbers again.
2. It deleted my master quotes document! Luckily, the raw text dumps are still in the `dumps/` folder. The files are named `dump_<ID>.txt` (the ID matches the CSV). My favorite quotes are buried in all that random text, but they *always* start with `[[` and end with `]]`. 
3. I need you to extract all those quotes and create a `recovered_quotes.json` file in the `./` folder. It needs to be a dictionary where the keys are the EXACT correct book titles (from the fixed catalog), and the values are lists of the quotes found for that book (but strip off the `[[` and `]]` brackets, please!).

I really need this to be perfect. I'll be reading a book to calm my nerves while you do this. Please save my job!
