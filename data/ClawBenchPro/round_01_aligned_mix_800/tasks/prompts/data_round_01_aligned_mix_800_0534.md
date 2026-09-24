Listen, I’m near my breaking point and I desperately need your help. As the operations manager here at the university, I try to keep things running like a well-oiled machine, but this recent 'Bird-Watching' and 'Ecology' community outreach program has turned into a total nightmare. 

Our legacy IT system crashed last month. Instead of a clean approved whitelist, I’ve got hundreds of fragmented approval JSON files scattered across the `approvals` directory by different departments. Volunteers often change their status, so you might find multiple approval slips for the same person. Only the slip with the *latest timestamp* dictates their final status! We are only concerned with folks who are officially `"APPROVED"` and whose assigned program is specifically either `"Bird-Watching"` or `"Ecology"`. 

To make matters worse, the volunteer sign-in sheets in the `field_logs` directory are a disastrous mix of different CSVs and JSONs from various field sites. Some logged their names, some logged their Volunteer IDs, and some logs aren't even for our outreach programs! We only care about activities where the task description explicitly contains the words "Bird-Watching" or "Ecology" (case-insensitive). Also, be warned: the hours they logged are full of typos, blanks, and absolute nonsense.

You'll need to cross-reference everything with our master roster in the `registry` folder. 

Here’s exactly what I need before my meeting with the Dean:
Please generate a strict JSON report saved at `deliverables/reconciliation_report.json`.
It must contain exactly two keys:
1. `"unauthorized_participants"`: A deduplicated, alphabetically sorted list of the names of anyone who participated in our specific programs but was NOT legitimately approved (if they logged an unknown ID that isn't in our roster, just use that string).
2. `"authorized_hours"`: A dictionary mapping the names of the officially approved volunteers to the total valid hours they spent on our specific programs (as floats).

Please cut through this chaos. My job is literally on the line here!
