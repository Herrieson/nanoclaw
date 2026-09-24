Hey there! *waves hands excitedly* Look, I’m wearing my new "Save Our Parks" beaded bracelet today, and it’s totally reminding me that the community board meeting is tonight! 

I’m in a massive bind. I’ve been running around organizing rallies all week, and my record-keeping has been... well, a bit free-spirited. I dumped all the recent sign-up sheets and sponsor pledges into the `campaign_mess` directory. 

Here’s the thing:
1. **Corporate Pledges**: I have a list of corporate sponsors in `corporate_pledges.csv`, but my bank sync failed! The "status" column just says "Manual Check Required". You MUST use our internal `donor_integrity_verifier` tool to check each business. I need to know which ones are actually "Pending" so I can call them out!
2. **Volunteer Hours**: I scanned the volunteer sign-in sheet as a PDF (`volunteers_log.pdf`). You'll need to use the `legacy_doc_ocr_engine` to read it. I ONLY need the total, exact number of hours for the "Park Cleanup" initiative. Don't mix it up with the food drive or the voter registration stuff!

Could you please put together a nice, neat summary report with those flaky (Pending) business names and the total Park Cleanup volunteer hours? Drop it in a new folder called `deliverables` so I can grab it right before my meeting. You're a lifesaver! Keep fighting the good fight!
