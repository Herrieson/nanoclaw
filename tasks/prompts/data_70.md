Oh my God, I am totally freaking out right now! My grant proposal is due tomorrow morning, and my local bioinformatics pipeline completely crashed while I was at the gym doing deadlifts. My cortisol levels are literally through the roof!

I have this `home_lab` directory where I dumped a bunch of files. Honestly, my file management is a total disaster right now. I know there are some sequence files in there, but I also left my gym logs, grocery lists, and God knows what else scattered in those folders. 

Look, I desperately need you to go into that `home_lab` directory and its subfolders. Find all the `.txt` files that actually contain sequence data. You'll know them because they have a header line starting with `>SEQ_` followed by the ID, and the next line is the actual nucleotide string (just a bunch of A, T, G, and C letters). 

I need you to calculate the GC-content for every sequence. It's super simple scientific stuff, I promise—just count the number of 'G' and 'C' letters, divide by the total length of the sequence, and multiply by 100 to get a percentage. I *only* care about the sequences where the GC-content is strictly greater than 55%. 

Please, please output a file called `high_gc_sequences.csv` directly inside the `home_lab` directory. It must have exactly two columns: `ID` and `GC_Content`. Oh, and make sure the `GC_Content` values are rounded to exactly 2 decimal places (like `80.00`). 

Don't mess this up, I really need this data for the in vitro section of my proposal!
