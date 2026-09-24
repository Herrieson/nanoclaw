Listen, I do not have the time or the mental bandwidth for this today. I am in the middle of pitching our new derma-tech R&D line to the board in two hours, and my phone is buzzing every thirty seconds because the junior marketing team completely imploded during the IT migration.

Instead of a clean spreadsheet, they left me an absolute catastrophic wasteland of data. They dumped a month's worth of raw, unaggregated daily influencer engagement logs into some folder, scattered the influencer identity mappings across hundreds of subdirectories, and somehow managed to mix up the legal compliance banlists. 

I am not manually sorting through this garbage, and I need you to clean it up *now*. Here is what I know:
1. **The Formula**: They left an email dump somewhere in the `communications` folder. Read it, find the *final* agreed-upon "True Impact Score" formula for Q3, and ignore their old drafts.
2. **The Logs**: The raw engagement logs are split into daily files. You have to aggregate the metrics for each influencer across all these days. Be warned: I saw them complaining about corrupted rows ("ERR", missing data), so your script better handle that gracefully without crashing.
3. **The Identities**: The logs only use some internal ID. The mapping to their actual names is blown to pieces in the `roster_database`.
4. **The Blacklist**: Legal left their banlists in the `compliance_department` folder. Because Legal is incompetent, there are multiple versions. **Only the most recent banlist matters** (check the Unix timestamp in the filenames). If an influencer is on that *latest* blacklist, they are completely disqualified, even if they have the highest score in the universe.

Figure out the total score for every influencer, filter out the blacklisted ones using the *correct* list, and give me the actual names of the **Top 3** valid influencers we should hire. 

I don't care about the file format, just make it readable. Create a new directory called `deliverables` and put your final top 3 list in there. Please, just write a robust script and get this done so I don't have to look at it again.
