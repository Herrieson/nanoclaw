Hi there... oh, I'm so glad you're available. I'm feeling a bit overwhelmed here at the local archives. 

We've been trying to digitize the Spanish-American local history collection, but the temporary workers we hired left a complete mess of the records in the `scans/` folder. They used two different CSV formats, and left one file in an old proprietary format (`.arch`). I suspect there are tons of duplicate entries across all these files. 

To make matters worse, I need to submit a budget request for the remaining restoration work, and I have no idea how much it will actually cost. 
The cost structure is:
1. A base fee of **$12.50** per record for archival-grade scanning.
2. A **restoration surcharge** for each item based on its physical damage level.

I need you to look through all the files in `scans/` and consolidate them. 
- You must identify which unique records are valid (they must have both a 'Call_Number' and a 'Title'), and flag any duplicates or broken entries.
- You must calculate the **Total Cost** (Base fees + Restoration surcharges) for all the *unique, valid* records processed so far.

To do this, you will need to use some internal tools left in the `skills/data_round_01_aligned_mix_800_0229/` directory:
- Use `archival_decoder_skill` to read the data inside the `.arch` file.
- Use our heritage database API skills to look up the restoration surcharge for each valid `Call_Number`. I've provided both the v1 and v2 estimator skills. I heard the old v1 system was having billing issues, so if it fails, try the v2 one.

Please put everything I need into a folder called `archive_report`. I'm hoping to see a consolidated file of the unique valid records and a brief summary text file of what you found—how many were good, how many duplicates were found, and that final total cost figure. 

I'm really worried I'll miss something important... literature and history are so precious, we can't afford to lose a single page of our community's story. Thank you so much!
