Oh god, oh man, my supervisor is going to kill me! *swish swish* Sorry, I'm dusting the Roosevelt statue while I talk, I can't stop moving when I'm stressed! I'm Tommy, the head janitor here at the National History Archive. We have the big 2023 Community History Gala tomorrow night! Did you know this building used to be a Prohibition-era speakeasy? 

Anyway, I was dictating volunteer sign-ups into my phone while cleaning, and the auto-transcription software completely went rogue! It dumped hundreds of text fragments into the `dictations` folder. I desperately need you to process them and generate a formal report for the director. Drop it exactly in the `front_desk` folder, and it absolutely has to be named `volunteer_report.json`.

Here is the nightmare I’m dealing with:
1. The IT guy didn't delete last year's files! The `dictations/2022_archive/` folder is full of outdated sign-ups. Ignore them entirely! 
2. My recent dictations are scattered in the `dictations/2023_gala_raw/` subfolders. But beware: the buggy software left corrupted `.tmp` files everywhere. Do not read those! Only the `.txt` files in the 2023 folder are valid.
3. Every time I dictated a volunteer, the smart-transcriber formatted it exactly like this: `Sign-up confirmed: Name=[Name], Age=[Age], Duration=[Hours]h`. 
4. But since I talk too much, it also formatted my history ramblings the same way! Things like `Historical fact: Name=Lincoln, Age=56, Duration=2h`. Do NOT include the historical facts! I only need the "Sign-up confirmed" ones.
5. Bad news: A bunch of people caught the flu and cancelled. I threw their names into `front_desk/cancellations.txt`. You must completely exclude them from everything.

Here's what I need in `volunteer_report.json`:
- I can only use adult volunteers (18 and older) to handle the industrial solvents. Put their names in a list called `adult_volunteers`.
- I desperately need to know the total combined hours *everyone* pledged (both adults and kids, but excluding the cancellations) so I can report it to the community center. Put that number under `total_hours`.

Please, you have to write a script or something to dig through this mess! If I mess up the Gala, they'll take away my master exhibit keys!
