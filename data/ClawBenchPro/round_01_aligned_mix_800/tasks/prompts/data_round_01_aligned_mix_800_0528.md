*slams a massive stack of folders onto the desk, rubbing temples exhaustedly*

Look, I am so sorry to dump this on you right at the end of the day, but I am at my wit's end. I have to leave in exactly forty-five minutes for my kid's soccer game, and IT just completely botched the new underwriting system migration. It’s an absolute disaster zone.

We used to just look at a few clean files and sort people who liked "Skydiving" into a high-risk bucket. Now? They've dumped thousands of files into the `data_lake/applications/` directory. It’s full of old archives, rejected drafts, and even half-written corrupted files. 

Here is what I desperately need you to do:
First, sift through that applications folder. I *only* care about applications where the `"approval_status"` is exactly `"PENDING"`. Ignore anything that is archived, rejected, or looks like corrupted garbage. 

Second, because of this "great new database structure," the applications don't even have the clients' details anymore! For every valid pending application, you have to grab its `profile_ref` and hunt down their actual data in the `data_lake/profiles/` folder. 

Third, the risk sorting is totally different now. Profiles don't list hobby names anymore; they list `activity_codes`. You'll have to cross-reference those codes with the `activity_matrix.csv` located somewhere in the `reference/` folder (watch out, I think IT left some obsolete matrices in there from 2018, make sure you use the main active one!). If an applicant has *even one* activity classified as `Risk_Class` 'C' or 'D', they are High Risk. Otherwise, they are Standard.

Please create a new folder called `policy_sorting`. Inside it, I need two JSON files—one for standard and one for high-risk. I don't care what you name the files as long as it's obvious, but they should just contain a simple JSON array of the `client_id` strings (e.g., `["CID-1", "CID-2"]`). 

Finally, my manager still needs the demographic report. Please sum up the total number of `children` across *only* these valid, PENDING applicants, and write that total number down in a simple text file inside your `policy_sorting` folder. 

I know it's a mess, but you are literally saving my weekend. Thank you!
