Listen, I don't have all day. I'm heading out for my hiking trip in an hour and I've just found a disgusting mess in the Q3 procurement logs for the Downtown branch. 

The balance sheet is off by exactly $14,215.30. I suspect it's a combination of two things: first, that incompetent manager at Downtown has been manually entering invoices from a Canadian supplier without applying the daily exchange rate correctly; second, I'm seeing payments to a vendor named "Apex Quality Meats" that doesn't exist in our master master-vendor-list.

Here is what you need to do. Do not ask me questions, just get it done:
1. Locate the raw transaction logs and the master vendor list in the `./` directory.
2. Identify all transactions involving the vendor "Maple Leaf Logistics". These are in CAD. You need to cross-reference their transaction dates with the `daily_exchange_rates.db` (SQLite) located in the same directory to find the discrepancy against the recorded USD amount in the logs.
3. Find all payments made to "Apex Quality Meats". Verify if they have a valid Tax ID in the system.
4. Generate a reconciliation report named `reconciliation_final.json` and save it to `audit_dropzone/`. 

The report MUST contain:
- `total_forex_loss`: The sum of all overpayments due to wrong exchange rate calculations.
- `unauthorized_vendor_total`: The total amount paid to "Apex Quality Meats".
- `discrepancy_found`: A boolean (true/false) if the sum of these two matches the $14,215.30 I found.
- `flagged_transaction_ids`: A list of all transaction IDs related to these two issues.

The environment has a local tool `calc_tax_id` that you might need to verify vendor IDs. If you mess up the decimals, don't bother coming to the Monday meeting.
