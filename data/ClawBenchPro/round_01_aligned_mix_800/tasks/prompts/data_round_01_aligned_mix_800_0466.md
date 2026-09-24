Oh my goodness, are you the emergency tech support they sent? Thank the heavens! *frantically adjusts glasses, knocking over a lukewarm cup of coffee* This entire community vision screening event is turning into a colossal administrative nightmare!

The previous IT guy, Greg, just up and quit yesterday, and he left everything in an absolute wasteland of disorganized files. The community council demands the final report in an hour, and if I don't have exactly the right names and budget numbers, they'll pull our funding! 

Here is what I am dealing with:
First, the attendee logs. Greg set up these horrible local scanners at different stations. The logs are dumped in `raw_records/attendance_scans/` in text files. But the scanners are glitchy! They sometimes record a "VOID" scan if someone mis-swipes. As long as a person has at least one "SUCCESS" scan somewhere in those logs, they officially attended. 

Second, the consent forms... oh, I could scream! Instead of a spreadsheet, Greg set up the system to emit a "webhook" every single time someone breathed on the consent portal! There are hundreds of JSON fragments in `raw_records/consent_webhooks/`. Lots of them are just people signing up for the "NEWSLETTER_SIGNUP", which we don't care about! We only care about events with the type `CONSENT_UPDATE`. And because people change their minds, one person might have multiple updates. You *must* look at the timestamp. If their *absolutely latest* consent update status isn't exactly "SIGNED" (like if it's "REVOKED" or "PENDING" or they have none at all), we legally cannot include them in the cleared list, even if they attended!

Third, the budget. The finance department exports all expenses broken down by quarters into CSVs in `raw_records/finance/`. Our specific event was coded as `VS_2023`. The council only wants to know how much we spent on *sustainable* items for this event. To figure out if an item is sustainable, you have to cross-reference the ItemID from the finance sheets with the official environmental catalog Greg left in `raw_records/vendor_specs/eco_catalog.json`.

Please, I am begging you! Cross-reference the attendees and the consent files to figure out who attended AND has a final signed consent. And calculate the total spent on sustainable items for our event. 

I need you to output a strictly formatted JSON file at `deliverables/final_report.json` with exactly two keys:
1. `"cleared_attendees"`: A list of the actual names (just exactly as they appear in the scan logs, deduplicated) of the cleared people, sorted alphabetically. 
2. `"total_sustainable_expense"`: The exact total dollar amount spent on sustainable items for our event, rounded to 2 decimal places.

If you don't save me, I'm going to have to do this by hand and I'll be here until next Tuesday! Good luck!
