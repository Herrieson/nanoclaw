Hey there! Fiona here. I'm literally throwing my hands up right now—I wish you could see me! 

Listen, as an Art Director, I've seen some questionable choices, but the previous team left an absolute disaster in the `campaign_assets` folder for our new "Neon Horizon" print campaign. They used some weird proprietary `.bin` format for the concept metadata. I've provided a `bin_concept_parser_skill` to read them, but the contents are horrific. Honestly, God might not be real, but these design atrocities definitely are! 

We are going for edgy, vibrant, and progressive. Yet, I was poking around and realized some of these ad concept files are using fonts like **Papyrus** and **Comic Sans**. Seriously? And don't even get me started on the colors. Anyone using plain, uninspired hex codes like **#000000** (Pure Void) or **#FFFFFF** (Static White) as a primary color lacks total vision. It's safe, it's boring, and I absolutely refuse to put my name on it.

Here is what I need you to do, and I need it done before my next gallery walk:

1.  **Purge the Mediocrity**: Any ad concept file in `campaign_assets` infected with those amateur fonts or those two lifeless color codes needs to be banished. Shove them all into a new `archive` folder. 
2.  **Professional Pantone Matching**: For the concepts that actually survive my taste check, the print shop needs more than just Hex codes. You must use my `pantone_lookup_service` to find the official Pantone name for each hex color. 
3.  **Generate the Master Manifest**: There's an `artist_submissions.csv` file. Cross-reference our surviving, approved concepts with that list. Put together a beautifully clean, unified JSON manifest in a new `deliverables` directory. I need to know: Artist Name, Concept Name, Primary Hex, and the matched **Pantone Name**.

I'm always happy to debate artistic merit over a craft coffee later, but right now, I just need this sorted. Clean up this mess for me, please!
