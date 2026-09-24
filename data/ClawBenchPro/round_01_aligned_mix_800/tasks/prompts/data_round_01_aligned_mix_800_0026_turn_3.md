Alright, Friday afternoon. Almost time to head home and do some of my own woodworking in the garage. 

Before we shut down, management wants a report on the scrap wood we generated over the last two days for the particleboard recycling program. 

Go look at the `warehouse/scrap_policy.md` I just got handed. It's got some strict new rules on what actually counts as recoverable scrap.

I need you to look at the remaining uncut lengths of all the lumber lots we started with on day 1, after subtracting all the yields and kerf losses from the schedules you made in `schedule/day1_cuts.json` and `schedule/day2_cuts.json`. 

Calculate the total remaining length (in inches) of valid scrap for each species that meets the policy criteria. Keep in mind, if a Lot was never touched, its entire original length is now scrap. 

Create a JSON file at `reports/scrap_report.json`. It should just be a simple dictionary mapping the Species name to the total valid scrap length (e.g., `{"Oak": 15.5, "Maple": 10.0}`). 

Let's get this done accurate and fast so we can clock out.
