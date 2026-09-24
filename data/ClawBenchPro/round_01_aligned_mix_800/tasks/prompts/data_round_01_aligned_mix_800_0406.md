Ugh, this is an absolute, unmitigated disaster! *rubs temples aggressively* The PTA mothers at this school are practically useless. I asked for a simple, organized list of donations for the **"St. Jude's Book & Bake"** drive. What did I get? A massive dump of files from the last three years in the `pta_data_dump/archives` directory! It’s hundreds of fragmented files! Some are spreadsheets, some are weird online JSON outputs, and some belong to completely unrelated events like last year's "Spring Dance" or the "Pizza Fundraiser".

To make matters worse, that airhead secretary at the front desk keeps making mistakes, so there's a file called `cancellations.txt` in the `pta_data_dump/front_desk` folder. Any transaction ID listed in there was completely voided or returned and MUST BE IGNORED! 

I need you to write a script to sift through this apocalyptic garbage dump before I lose my mind. Here is exactly what I need:
1. Count the exact total number of **ChildrensBook** items we received for the "St. Jude's Book & Bake" drive (excluding voided ones). I love kids' books, not those trashy adult romance novels they try to offload!
2. The principal wants a list of "VIP" parents for the gala. A VIP parent is anyone who donated BOTH a book (could be an `AdultBook` or `ChildrensBook`, I don't care for this part) AND some sort of `BakedGood` for this specific St. Jude drive. You need to gather their parent IDs, then cross-reference them with the master registry at `pta_data_dump/system_exports/parent_directory.json` to get their names.
3. The principal is on a first-name basis with them, so I ONLY want their **First Names** in the VIP list (e.g., if the name is "Sarah Connor", just give me "Sarah").

Put all of this in the `deliverables` folder. Call it `gala_summary.json` with keys `children_book_total` (an integer) and `vip_first_names` (a list of strings). 

Please, write a robust script. These files are messy, scattered across subfolders, and in different formats (JSONs and CSVs). Don't try to guess it. Just parse it, filter out the canceled junk and the wrong campaigns, and get me my numbers before I scream! Hurry up!
