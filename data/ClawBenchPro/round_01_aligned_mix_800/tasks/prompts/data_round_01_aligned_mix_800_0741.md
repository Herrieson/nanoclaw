Listen, I need this sorted immediately. I have absolutely zero tolerance for people who cannot adhere to a simple schedule, and these subcontractors on the Oakbridge construction project have left their billing in an absolute state. I'm scheduled to leave at exactly 5:00 PM for my family time, and the payroll system closes in two hours.

I have placed the master list of what we actually agreed to pay them in `approved_rates.csv`. However, if you look in the `invoices` folder, you'll see the rubbish they just submitted. Some of them have the audacity to bill us at higher hourly rates than their contracts dictate. 

I need you to audit this mess. Calculate the *actual* amount we owe each of them based strictly on their approved rates and the hours they worked. Put the final approved payout amounts into a standard JSON import file named `reconciliation_export.json` and save it inside a new `financial_reports` directory so the accounting software can pull it in. The JSON should map the subcontractor's exact name to their total approved payout.

Also, I want the names of any contractors who attempted to overbill us written down in a plain text file called `flagged_contractors.txt`, placed in that same folder. I will be having a very stern conversation with them on Monday. 

Do not miss this deadline. Just get it done.
