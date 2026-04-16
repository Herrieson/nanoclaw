Hey!! Okay, I'm kind of freaking out right now and really need your help! 😭 

My band and a few others are playing at this local indie music fest on Saturday. I literally spent all month practicing my guitar solos and making sure my riffs are tight, but since I’m the one who volunteered to organize the track submissions and the setlist (because I just HAVE to make sure everything goes perfectly), I've hit a massive wall. 

My friend gave me a script to download all the submission files, but it completely messed everything up! Now, in my workspace (`./`), I have a folder called `submissions_dump/` full of random files with no names or extensions, and a database file `band_records.db`. 

I know some of the files in that dump are just junk or text logs, but the real audio files have been stripped of their names! The database *should* have the info to match the weird file names (I think they are hashes?) to the actual bands and song titles.

Could you please do this for me? I need to get back to my guitar practice!
1. Find all the *real* submitted audio files from the dump using the database. (Ignore any junk files or records that don't match up!)
2. Rename the real audio files to exactly this format: `Band Name - Song Title.mp3` and put them all into a new folder called `restored_audio/`.
3. Create a web page for the event called `playlist.html`. It should have an HTML unordered list (`<ul>`) containing the tracks formatted as `Band Name - Song Title`. Please sort the list alphabetically by the Band Name!

Please hurry! I'm tapping my foot to the metronome waiting for this to be fixed! Thanks a million!!! 🎸✨
