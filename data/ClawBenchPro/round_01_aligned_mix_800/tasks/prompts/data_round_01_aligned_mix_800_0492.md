Oh heavens, I am in such a terrible bind! I was just out back tending to my hydrangeas when my husband reminded me that the school district's library audit is this coming Monday. Being a local government employee has its perks, but these audits are just dreadful. I’ll admit, I’ve been incredibly scattered lately—between church activities and my family, I haven't been keeping the library files very tidy. 

Here is the crisis: some careless middle schoolers checked out my precious restricted antiques, and they are hopelessly overdue! Anything that was supposed to be returned strictly before October 1st, 2023, is officially overdue. 

I need you to comb through this absolute nightmare of a file system for me. Here are some clues to help you navigate my mess:

1. **The Restricted List**: The IT department dumped all my old configuration backups into the `sys_configs/` directory. There are dozens of junk JSON files in there, but I know for a fact that the true, active list of antique books is inside the only file that contains the key-value pair `"status": "active"`. The restricted book IDs are listed in there.
2. **The Checkout Logs**: I hate typing, so I use a voice transcriber every day. The logs are shattered across the `voice_transcripts/` directory, organized by month and day. It's mostly me rambling about my garden, but I strictly use the exact phrasing `Student [Name] insisted on checking out [BookID]` and `due date to [YYYY-MM-DD]` when a book leaves. 
   **WARNING**: You must also check if they brought it back! When they do, my software transcribes it exactly as `Good news, [BookID] was returned`. If a book was returned, do NOT count it as overdue, regardless of the date!
3. **The Replacement Costs**: The district's purchasing department is completely incompetent. They split the library inventory across hundreds of CSV files inside `district_procurements/`. The column headers are wildly inconsistent, but if you find the row with the restricted BookID, the price will be there (often riddled with currency symbols, extra spaces, and commas). 

Please figure out exactly which students are currently hoarding my unreturned, overdue antique books, and tally up the total replacement cost for those specific missing treasures so I can send a very strongly worded letter to their parents.

Compile whatever you find into a file named `overdue_antiques_report.json`. The JSON should contain a list of the delinquent students' names (duplicates are fine or you can deduplicate, I don't care) and a field with the final total replacement cost (as a single numeric value). I really need to get back to my gardening before church, so please, just handle this!
