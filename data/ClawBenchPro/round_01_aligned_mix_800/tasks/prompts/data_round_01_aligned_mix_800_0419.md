Hey, it's Marcus. *exhausted sigh* I am literally up to my neck in concrete dust, scrap metal, and toddler toys. I am losing my mind. 

I thought I was being smart by using a new cloud-sync scanner app for all the receipts and site logs that were overflowing in my truck's glovebox. Instead, the app went berserk. It shredded my entire life into hundreds of fragmented files and dumped them all into a nested labyrinth under the `sync_dump` directory. 

I need you to salvage this before the city inspector fines me into oblivion tomorrow, and before my accountant drops me as a client. 

First, the safety inspector. The app dumped all my daily logs into `sync_dump/site_records/`. There are hundreds of them. 
I ONLY care about logs where the `Inspector` is exactly `Marcus` and the `Status` is exactly `Finalized`. Ignore everything else (drafts, my foreman Dave's notes, etc.). The logs don't say if a hazard is critical anymore; they just have an `Incident_Code`. You'll have to cross-reference those codes with the official manual I uploaded to `compliance/safety_matrix.json`. Find the incidents that correspond to Severity Level 4 (Critical) or Severity Level 5 (Immediate). Extract those specific `Incident_Desc` descriptions and save them into a file.

Second, the accountant. My financial life is scattered in `sync_dump/financials/` as hundreds of JSON fragments. 
To keep the IRS happy, I strictly use my business credit card ending in `4921`. If a transaction doesn't explicitly have `card_last4` as `4921` AND a `status` of `POSTED`, it's not going on this report. The receipts only show a `vendor_id`. My accountant sent me a mapping file located at `accounting/vendor_categories.csv`. I need you to calculate the exact total dollar amounts I spent specifically on the `Construction` category, and separately, the `Art` category. 

Please, do me a massive favor. Create a folder called `ready_for_monday`. 
Put the safety hazard descriptions into `ready_for_monday/critical_hazards.txt` (just the descriptions, one per line is fine).
Put the expense math into `ready_for_monday/expense_totals.txt` (clearly showing the total for Construction and the total for Art).

I've got to go scrape paint off my four-year-old. I am completely counting on you to navigate this mess.
