Good morning. I need a SITREP on this historical data ASAP. 

I'm putting together a briefing on Native American tactical communicators for my kids' school history month, but S-6 dumped a complete cluster of raw files into my workspace. My ROE (Rules of Engagement) for you are simple:

1. Look in the `./` sector. You'll find an archive called `comms_dump.tar.gz` and a local database `historical.db`.
2. I only care about personnel whose Role is specifically designated as "Code Talker".
3. For every "Code Talker" record you can dig out of those logs (watch out, some of the S-6 guys encode their files or leave things in weird formats), cross-reference the listed "Commander" with the `officers` table in `historical.db`. 
4. If the Commander actually exists in our historical database, extract the Operation name, Unit, and Commander.
5. Compile the validated targets into a clean `SITREP.json` file in the `./` directory. The format should be a JSON array of objects, each containing keys: "Operation", "Unit", and "Commander".

I have to get the kids to their soccer practice, so I'm trusting you to execute this mission parameters without me holding your hand. Dismissed.
