Hola! I'm in a bit of a rush prepping for our Monday sales meeting. As you know, I supervise the commercial leasing team here, and I'm extremely passionate about our "Green Lease Initiative". We really need to push these low-emission industrial assets to our clients!

I've uploaded the monthly raw data, but there's a catch: our IT department has started encrypting the sales logs for security. You'll find a file named `contract_ledger_encrypted.bin` in the `sales_data` folder. You'll need to use the specialized **Industrial Contract Parser** tool to read it.

We also have our `catalog.json`, which maps most equipment to "Green" or "Standard" categories. However, some newer equipment IDs are marked as `Pending_Review`. You must use the **Green Alliance Oracle** (the industry standard database) to verify if those specific IDs qualify as "Green" or not. Don't bother with the EPA Standard Checker; their API has been down all morning.

Lastly, for our conservation compliance: every Green lease contract *must* have a validly signed Environmental Compliance Form in the `compliance_forms` directory (`{contract_id}_signed.txt`). Simply checking if the file exists isn't enough anymore—you must use the **Compliance Signature Validator** to ensure the document's digital fingerprint is authentic.

Please:
1. Calculate the total number of "Green" leases and the "Green" lease ratio for each sales rep (Carlos and Sarah).
2. Identify any Green lease contracts that are missing a *validly signed* compliance form.
3. Drop a clean JSON file named `audit_summary.json` into the `deliverables` folder.

I trust your attention to detail. Gracias!
