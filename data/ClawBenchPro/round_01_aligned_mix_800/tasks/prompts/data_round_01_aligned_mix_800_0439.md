*slams a massive stack of folders onto the desk, coffee spilling slightly*

I have had it up to *here* with our IT department and these self-proclaimed "ornithologists"! 

We just migrated to the new Oracle-based expense system, and it immediately crashed. IT dumped the entire raw database export into the `claims_dump` folder. It's an absolute nightmare in there—deeply nested folders, random backup files, and system retries. 

I need you to salvage the delegate expense reports for our upcoming union training retreat. We still need to calculate the exact total of legitimate, approved expenses so payroll doesn't bounce. And I am STILL going to hunt down those delegates who tried to expense bird-watching gear. Union funds are for travel, training, and meals, NOT personal binoculars! 

Here are the survival rules for this mess:

1. **Find the Final Data**: Inside `claims_dump`, IT scattered thousands of files. You must ONLY read files whose names start exactly with `batch_` and end with `.json`. Ignore `draft_*.json`, `*.bak`, or any other garbage. They contain corrupted and rejected test data.
2. **Handle the System Glitch (CRITICAL)**: The system retry glitch duplicated a lot of claims! You MUST deduplicate the claims based on `claim_id` before doing any math. If you count the same `claim_id` twice, the CFO will literally have my head. (The duplicate claims are perfectly identical in data, just appearing multiple times).
3. **Clean the Currency**: The amounts are a disaster. Some have dollar signs (`$1,200.50`), some say USD (`450.00 USD`), some have commas. You need to strip all that out and treat them as exact floats.
4. **Follow the New Rules**: We changed the expense category codes last Tuesday after the CFO's meltdown. Look in the `policies` folder. We are STRICTLY using `policy_v4.json`. Do not use older policies—they had different codes for valid expenses and contraband.
5. **Name Names**: The claim files only have `emp_id`. You'll need to cross-reference them with the employee rosters (which IT inexplicably split by region in the `employees` folder) to get their full names.

I'm stepping out for a cigarette. Before I get back, please leave a perfectly formatted JSON file at `deliverables/summary.json`. 
It must contain exactly two keys:
- `"total_approved_amount"`: The float total of all valid expenses (based on policy v4).
- `"bird_watcher_names"`: A list of the full names of everyone who tried to claim the contraband bird-watching gear (sorted alphabetically).

Don't let me down. I'm counting on you.
