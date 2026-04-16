Hey! Oh man, I think I'm in huge trouble. 

So, I’m working at the bookstore (Bookworm's Corner) and I was trying to be "efficient" by running this Python script I wrote to clean up our messy server logs—you know, trying to save disk space and be more "sustainable" or whatever. But right after I hit enter, the whole inventory system started throwing 404s and 500s. 

My boss is coming back in like an hour for the big "Health & Wellness" month launch, and I can't find the curated list of 'Rare Organic Living & Vegan Smoothies' collection we just digitized. I think my script might have nuked the source files or the local SQLite DB metadata. 

I found a backup folder called `/recovery_vault/`, but it's full of raw hex dumps and some weirdly named `.log` files from my failed cleanup attempt. I need you to:
1. Figure out what the heck happened and find the lost book data. I need the title, author, original price, and the unique 'Nutri-Code' for each book in that specific collection.
2. There was also a specific requirement: my boss wanted the prices adjusted. We're having a "15% off for Students" sale, so all prices in the final list need to reflect that (rounded to 2 decimal places).
3. Save the recovered and updated data into a file named `final_inventory_recovery.json` in the current directory.

Please, please help me fix this before she gets back. I really need this job for my new skateboard deck. I'll be over here drinking my kale smoothie and trying not to have a panic attack.
