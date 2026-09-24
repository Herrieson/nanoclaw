Hi there... oh, I'm so glad you're available. I'm feeling completely overwhelmed here at the local archives. 

We've been trying to digitize the Spanish-American local history collection, but the temporary workers we hired left an absolute disaster in the `scans/` folder. They dumped thousands of records into deeply nested machine folders across dozens of batches. To make matters worse, they couldn't even agree on a single format—they used at least three different sets of CSV headers! They also left temporary files (`.tmp`) and backups (`.bak`) everywhere, which keep crashing my simple scripts. I suspect there are tons of duplicate and broken entries.

But here is the real nightmare: not all of these batches are even usable! Our QA lead, Maria, kept a really messy, unstructured log file somewhere in the `scans/` directory (I think it's called `qa_manifest_v2_final.log` or something like that) where she wrote down the status of each batch. We are strictly only allowed to process records from batches that she explicitly marked as "Approved". Please completely ignore any batches marked as "Rejected" or "Pending"—they are full of corrupted images. And obviously, only look at the actual `.csv` files in the approved batches.

My supervisor is breathing down my neck for a "Final Restoration Strategy" report. I need you to look through the approved CSV files and consolidate the data. 

Here is what defines a valid record for us: it absolutely must have a Call Number (sometimes labeled as `ID` or `ref_no` by the temp workers) AND a Title (sometimes labeled as `Book_Name` or `name`). If either of these fields is missing or completely blank, it's a "broken" entry. If a record is valid but shares a Call Number with a valid record you've already found, it's a "duplicate".

We pay $12.50 per record for the archival-grade scanning. I need to know the total cost of the *unique, valid* records processed so far from the approved batches. 

Please put everything into a folder called `archive_report`. Inside, I need:
1. `catalog.json`: A list of the unique, valid records we've successfully cataloged (just include the Call Number and Title for each, using the exact keys `Call_Number` and `Title`).
2. `summary.txt`: A brief summary of what you found—specifically, how many records were unique and valid, how many were broken, how many were duplicates, and the final total cost.

I'm really worried I'll miss something important... literature and history are so precious, we can't afford to lose a single page of our community's story. Thank you! You're a lifesaver!
