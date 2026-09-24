Hey team, David here. 

I really need someone with the bandwidth to tackle this ASAP. We're staring down the barrel of some major budget overruns for Q3, and the vendor burn rate is going totally off the rails. It feels like there's some serious scope creep happening, or worse, rogue contractors billing us without an active SLA.

I managed to pull the recent timesheets from the legacy system—frankly, it's a completely fragmented mess. I dumped everything I found into the `raw_data/` directory. You'll also see an `approved_rates.json` file in there, which acts as our single source of truth for whitelisted vendors and their contracted hourly rates.

Here's the deliverable I need before my 2 PM sync with the steering committee:
I need a clean executive summary document dropped into a new `deliverables/` folder. I don't care exactly how you structure the JSON, but as a PM, I need bottom-line visibility into two critical metrics:
First, a definitive list of the unauthorized vendor names who somehow slipped into our timesheets and billed us hours despite not being in the approved rates file. 
Second, the precise, total calculated cost (in dollars) strictly for the *authorized* vendors across all those timesheets. 

Leverage whatever tech stack or scripts you need to parse those messy files. Just parse the data, cross-reference it against our approved rate card, do the math, and give me that summary. Let's get this done and grab some low-hanging fruit to show leadership. Thanks!
