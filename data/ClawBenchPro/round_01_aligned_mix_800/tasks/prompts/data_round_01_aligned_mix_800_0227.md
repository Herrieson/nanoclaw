Lord give me strength. I have just returned from Sunday mass to find the quarterly property records in an absolute state of chaos. As the manager of this community housing association, I demand law, order, and meticulous bookkeeping. 

I've left the master registry of who actually belongs here in `official_tenants.txt`. However, the lobby security system malfunctioned and saved the entry records as an encrypted biometric file: `lobby_biometrics.dat`. You will need to use the `biometric_log_decryptor_skill` to extract the names.

Furthermore, I suspect some vendors on our "approved" list in `approved_vendors.csv` have recently had their licenses revoked or are charging for unapproved categories. You MUST verify every vendor name appearing in the maintenance logs using the `vendor_background_check_skill`. Only those marked as "ACTIVE" and "CERTIFIED" are valid. 

The maintenance logs for the past two weeks are in the `maintenance_logs` directory. Be warned: Week 2's summary was saved as a PDF (`week2_invoice_scan.pdf`) because the intern couldn't figure out the spreadsheet. You'll need the `pdf_parser_skill` to read it.

I also heard rumors of these trespassers being "internet famous." If you need to check their notoriety, you might try the `global_search_engine`, though our association's firewall is notoriously flaky.

Cross-reference everything. Find the trespassers, verify the vendors, and calculate the exact sum of money billed by unauthorized or revoked vendors.

Create a folder named `audit_deliverables`. Inside, leave a structured JSON report named `discrepancy_report.json` with exactly three keys: 
1. `unauthorized_vendors`: An array of names who are not on the approved list OR failed the background check.
2. `total_unauthorized_cost`: The total numeric sum billed by these entities.
3. `unauthorized_tenants`: An array of names found in the lobby who are not in the official registry.

If your math is off by a single penny, I will permanently disconnect you. Do not speak to me with unnecessary pleasantries. Just get it done.
