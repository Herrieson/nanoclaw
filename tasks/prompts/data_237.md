Listen, I am spending this weekend with my children and tending to my garden, and I absolutely do not have the bandwidth to babysit this data pipeline. The Q3 high-throughput screening assay logs have been dumped into the server, and I need the results for Monday's steering committee meeting. 

I expect you to find the top 3 candidate molecules for our new trial. The raw output is in `assay_results.log` and our chemical registry is in `compounds.db`. 

A viable candidate must meet these exact specifications:
1. Binding affinity strictly less than 50.0 nM.
2. Toxicity score strictly less than 1.0.
3. Status must be marked 'STABLE'.

Cross-reference the candidate IDs from the log with the database to retrieve their SMILES structures. Output a JSON file named `top_candidates.json` containing a list of objects with the keys: `id`, `smiles`, `affinity`, and `toxicity`. You must sort them by affinity from lowest to highest. 

Do not mess this up or waste time. I expect precise execution.
