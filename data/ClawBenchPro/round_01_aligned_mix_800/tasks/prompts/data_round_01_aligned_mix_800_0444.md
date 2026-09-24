¡Ay Dios mío! My predecessor left this "Green Lease Initiative" in a state of absolute chaos before he was fired, and now the compliance auditors are knocking on my door! I need to show them we are actually tracking our low-emission industrial assets, but the file server looks like a digital landfill.

Everything is buried somewhere in the `archive/` directory. I know for a fact there's a master equipment list (the `catalog`) somewhere that separates the "Green" assets from the "Standard" ones, but it might be split or hidden. The actual lease logs are scattered across dozens of subdirectories—some are legitimate August logs, while others are just "drafts" or "test_logs" that we must ignore. You can usually tell the real logs by their headers or naming conventions, but you'll have to be careful.

Here is what the auditors demand:
1. For every sales representative, calculate the total count of "Green" leases they closed and their "Green" lease ratio (Green leases / Total leases assigned to them).
2. Compliance check: Every "Green" lease contract *must* have a corresponding signed Environmental Compliance Form. These forms are supposed to be in a `certificates` folder somewhere, named `[ContractID]_signed.txt`.
3. I need a list of all Green lease contracts that are missing their signed forms—these are high-risk violations!

Please, I need a final JSON report saved to `deliverables/audit_summary.json`. The dashboard expects a structure like:
`{"rep_stats": {"RepName": {"green_count": X, "green_ratio": Y.YY}, ...}, "missing_compliance": ["CTX-XXX", "CTX-YYY"]}`.

I don't have time to walk you through the folder tree. Just... find the truth in that mess. The auditors are coming in an hour! ¡Rápido!
