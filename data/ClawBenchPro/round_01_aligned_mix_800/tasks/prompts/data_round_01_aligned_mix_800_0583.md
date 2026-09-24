Yo... I am literally on the verge of a breakdown here. Thank you for answering my SOS. 

I took over the 2024 Spring Community Garden Drive because the last coordinator rage-quit, and left the data in absolute shambles. I thought I just needed to review a simple signup sheet, but the previous guy fragmented everything into this archaic multi-system nightmare!

Here is the deal: our progressive zero-waste initiative is strict. People MUST bring a reusable water bottle. Also, for insurance, no one under 16 can volunteer this year (it is 2024, so they need to be born in 2008 or earlier). 

But finding this out is a disaster:
- The volunteer profiles are scattered in dozens of JSON files inside the `registry/` folder. And half of them have a `status` of "withdrawn" or "banned", so please only look at the "active" ones!
- Their committed hours? Hidden in a massive spreadsheet somewhere in `planning/`, which also tracks a bunch of randos who didn't even finish registering. Total hours for a person is their shifts multiplied by hours per shift.
- The water bottle thing... oh god. The security team didn't write "bottle". They used product codes in their `checkpoints/` daily logs. You'll have to figure out which item codes mean "reusable water bottle" by looking at the `assets/equipment.yaml` catalog. If an active volunteer's ID shows up in *any* gate log with the right item code, they pass the zero-waste check.

I'm begging you. Cross-reference all this junk. Weed out the kids, the plastic-bottle users, and the inactive dropouts. 

Once you have the surviving elite, drop a clean JSON file named `ready_volunteers.json` into a new `deliverables` folder. I need two things in it: `names` (a list of their actual names) and `total_combined_hours` (the grand total of all the hours these approved people committed to).

I'm going to take an aspirin. Good luck diving into this digital wasteland.
