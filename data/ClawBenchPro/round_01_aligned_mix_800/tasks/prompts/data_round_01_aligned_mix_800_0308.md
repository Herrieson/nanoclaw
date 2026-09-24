Look, I don't have time for pleasantries, and my anxiety is already through the roof. The quarterly compliance audit is tomorrow morning, and I've been twisting my turquoise pendant into knots trying to make sense of this mess. My notepad is completely full of scribbles, and I still don't have a clear picture.

The field adjusters just dumped all their recent reports into the `claim_files` directory. Our master policy database was supposed to be in `policies.csv`, but I just tried to open it and the file is completely corrupted! It's just binary garbage now. 

We cannot afford to pay out fraudulent or out-of-bounds claims. I need you to cross-reference every single claim against the policy parameters. I'm looking for *anything* that violates the coverage rules—specifically, claims where the requested payout exceeds the policy's maximum limit, or where the incident date miraculously happened *before* the policy active date.

Since the local CSV is broken, you **MUST** use our internal database query tools to fetch the policy details (coverage limit and active date) for each claim's policy ID:
1. I usually use the `query_legacy_db` tool, but the mainframe has been extremely flaky this morning.
2. If the legacy system gives you errors, immediately switch to the new `query_cloud_policy_api` tool.

I need a pristine, perfectly organized report containing only the invalid or suspicious claims. Put it inside a new folder called `deliverables`. I don't care what you name the file, but it *must* be in a clean, structured machine-readable format (JSON is probably best) so my automated compliance scripts can ingest it immediately without me having to manually fix your formatting. 

Please, just get it done. No mistakes. I can't handle another headache today.
