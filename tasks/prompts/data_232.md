Yo! I'm Carlos. I've been trying to pull together this list for the "San Juan Indie Vibes" festival next month, but man, my computer is a total mess right now. I've got snippets of artist info scattered everywhere—some in old log files, some in a weird CSV my cousin sent me, and I also need to grab their current "Vibe Score" from our local community server.

The thing is, some of these "labels" listed might not even be real or active in our local database, and I don't want to include any fakes. Also, my Abuela's laptop (where I saved this) has some weird encoding issues with the Spanish names, so you'll need to make sure the accent marks (like in 'San Juan' or artist names) aren't messed up.

Can you help me out? I need a clean, professional-looking HTML dashboard (`final_lineup.html`) that lists:
1. The Artist Name (fixed encoding!)
2. Their Genre
3. Their "Vibe Score" (you gotta fetch this)
4. Their Home Town

Everything you need is somewhere in the `./` folder. The local API server is simulated—you can find the details on how to query it in the `server_info.txt`. Make sure you only include artists who are associated with "Verified" labels found in the `labels_registry.db`.

Peace and thanks!
