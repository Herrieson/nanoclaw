Hey there! I'm Danny. *fidgets with apron strings* Wow, it’s going to be a crazy Friday night at the restaurant, and I really need to get organized before the doors open. I love talking to everyone who sits at the bar, but right now the morning crew left things a total mess.

I’ve been practicing some cocktail mixing at home, and I wrote down three original recipe names in `recipes/titles.txt`. However, I forgot to write down the exact ingredients for all of them! Can you use the `search_cocktail_db_skill` to find the standard ingredients for those drinks?

Also, the morning stockroom log is in `stockroom_logs/morning_inventory.txt`. But wait—the manager left me a voice memo (`stockroom_logs/manager_note.mp4`) because he was too lazy to write down the last-minute delivery cancellations. You'll need to use the `audio_transcriber_skill` to hear what he said. I only want to pitch the drinks that we currently have *all* the ingredients for.

Oh, and the money part! The shift closing export from yesterday is in `pos_data/shift_closing.csv`. Please calculate my total tip cut (look for "Danny"). But here's the catch: the bar has a new "Clean Air Tax" on tips this week. Once you have my total gross tip, you *must* use the `bartender_tax_calculator_skill` with the `tax_rate` of 0.12 to find out my final take-home amount.

Once you have the winning cocktail(s) and my exact net tip total, please write it all up in a neat, professional-looking document and save it in a brand new folder called `prep_work`. I need to hand this to my boss in 10 minutes. You're a lifesaver!
