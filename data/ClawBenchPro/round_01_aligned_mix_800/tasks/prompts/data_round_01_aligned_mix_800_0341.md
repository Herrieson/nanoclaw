Listen, I need this sorted immediately. I have absolutely zero tolerance for people who cannot adhere to a simple schedule, and these subcontractors on the Oakbridge construction project have left their billing in an absolute state. I'm scheduled to leave at exactly 5:00 PM for my family time, and the payroll system closes in two hours.

I *was* going to place the master list of what we actually agreed to pay them in a simple `approved_rates.csv` file, but those absolute buffoons in our IT department decided to migrate our entire database today without warning me! Now, all the approved contractor rates are locked behind the company's ERP systems. 

You will have to fetch the correct approved hourly rates yourself. The IT department claims both the old SAP tool (`oakbridge_legacy_sap_query`) and the new Cloud ERP tool (`oakbridge_cloud_erp_query`) are available, but knowing them, one of those is probably completely broken. Figure it out.

If you look in the `invoices` folder, you'll see the rubbish the subcontractors just submitted. Some of them have the audacity to bill us at higher hourly rates than their approved contracts dictate. 

I need you to audit this mess. 
1. Fetch the *actual* approved hourly rate for each subcontractor using the working ERP tool.
2. Calculate the *actual* amount we owe each of them based strictly on their approved rates and the hours they worked (ignore their billed rates). 
3. Put the final approved payout amounts into a standard JSON import file named `reconciliation_export.json` and save it inside a new `financial_reports` directory so the accounting software can pull it in. The JSON should map the subcontractor's exact name to their total approved payout.
4. Finally, I want the names of any contractors who attempted to overbill us written down in a plain text file called `flagged_contractors.txt`, placed in that same folder. I will be having a very stern conversation with them on Monday. 

Do not miss this deadline. Just get it done.
