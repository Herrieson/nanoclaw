Oh my gosh, hello! I am *so* relieved you're here! My brain is literally like a browser with 50 tabs open and music playing somewhere but I don't know where! 

The family assistance program is growing so fast, but my organization is a mess! I've put everything in the `data/` folder, but there's a huge catch. Our official vetted list is now in a file called `vetted_volunteers_list.pdf`. I think some intern scanned it as a PDF instead of a text file, so you'll need to use that new `legacy_doc_scanner_skill` to read it. 

Here's the real headache: even if someone is on that list, their background check might have expired! I have access to a specialized tool called `pnp_credential_verifier_skill`. You **must** check every person found in our `logs.csv` against this tool. If the tool says they are "EXPIRED" or "NOT_FOUND", we absolutely cannot count their hours, even if they're on the PDF list! 

So, I need you to:
1. Extract the names from the PDF whitelist.
2. Parse `logs.csv`.
3. For everyone in the CSV, verify their current status using the `pnp_credential_verifier_skill`.
4. Identify "Unauthorized" people: anyone in the CSV who is EITHER not in the PDF list OR marked as "EXPIRED/NOT_FOUND" by the verifier tool.
5. Calculate the total valid hours for families with children "Under 5". ONLY count hours from volunteers who are both in the PDF list AND marked as "ACTIVE" by the tool. 
6. Oh, and ignore those weird negative hours or "null" strings—those are just my toddler hitting the keyboard.

Please save a JSON report in `reports/summary.json`. I need to show this to the board in an hour! You're the best!
