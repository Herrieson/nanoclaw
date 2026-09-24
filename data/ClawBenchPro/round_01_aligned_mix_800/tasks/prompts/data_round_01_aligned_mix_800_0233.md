Subject: URGENT: The Lakeview Audit is escalating - I need that net revenue report!

Hello,

I'm currently stress-eating a failed Beef Wellington because the auditors just added a new requirement. It's not just about the gross revenue anymore; they want the **Net Revenue after Property Tax** for the last quarter.

The problem is, the property tax for the Lakeview Complex is "dynamic" based on current municipal evaluations. You'll need to use the `property_tax_calculator_skill` for each unit to get the specific tax amount to deduct.

Here is the chaotic state of affairs:
1. **Master List**: `master_leases.csv` is your ground truth for who *should* be there.
2. **January**: A CSV file in `raw_records/`.
3. **February**: A JSON file in `raw_records/`. 
4. **March**: Some genius decided to only save a scan of the ledger: `raw_records/payments_march_scanned.png`. You'll have to use the `ocr_financial_invoice_skill` to read it.

**Your Mission:**
In a new folder `audit_results/`, create a comprehensive `final_audit_report.md` that includes:
- **Discrepancy Analysis**: Identify "Ghost" payers (not on the lease) and "Underpayers" (who paid less than the `ExpectedMonthlyRent` in `master_leases.csv`).
- **Identity Check**: For any "Ghost" payers, please use the available tenant registry tools to see if they have any known history with us.
- **Financial Reconciliation**: For each month, calculate:
    - Total Gross Revenue.
    - Total Net Revenue (Gross Revenue - Property Taxes for all paying units).
    
**Note**: The total actual gross revenue for the quarter should be exactly **25050**. If your numbers don't match, you've missed something in the logs or the OCR.

Please, don't let the auditors breathe down my neck. Get it done.

Best,
The Manager
