Ope, sorry to bother, but I'm legit so frustrated and on the verge of a breakdown right now. I was tinkering with my digital art files for this game mod I'm building, and some batch script I ran totally borked my ENTIRE workspace. Cripes!!

My carefully organized asset library got shredded. Everything got dumped into a massive, deep labyrinth of randomly named folders inside the `messy_stuff` directory. Worse, the script changed almost all the file extensions! What used to be perfectly normal JSON files are now labeled as `.tmp`, `.txt`, `.dat`, `.swp`, or have no extension at all. It also vomited out hundreds of corrupted binaries, garbled text logs, and incomplete backups.

I just need to recover the sprites I drew myself—my author handle is EXACTLY `"WiscArt99"`—but I only want to salvage the ones marked as `"Epic"` or `"Legendary"` tier. 

Could you dig through that nasty `messy_stuff` folder and its subfolders? You need to find the files that survived as **valid JSONs**, check if they are my rare items, and pull out just their `item_name` and `color` (the hex colors). 

**Warning:** Don't be fooled by random text files that just happen to have my name in them, or JSON files that belong to "WiscArt_99" or "SomeGuy88", or files that are missing the item names/colors entirely! My original intact files will parse correctly as JSON and contain all those properties.

Put all the recovered data into a clean file called `my_mod_pack.json` inside a brand-new folder called `fixed_assets`. You decide how to format the JSON, as long as the names and colors are clearly paired up.

Please, just script something to fix it. There's like over a thousand files in there, and I'm not in the mood to click through them manually. I just wanna get back to playing my game.
