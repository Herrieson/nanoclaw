Oh my god, my head is spinning... *taps fingers frantically on the desk*. I'm Clara, the production manager here. My morning yoga session did NOT calm me down today. We have to schedule three bands this week (Monday to Friday, we operate exactly 09:00 to 17:00 daily). The bands are 'The Lunar Tides', 'Neon Monks', and 'Crimson Dawn'. Their specific request files are scattered in the `requests` folder. Our staff info is in `staff/engineers.csv` and studio default gear is in `inventory/studios.json`.

Listen, I'm terrified of double-booking, overworking our people, or messing up special requests. Here are my strict rules:
1. ABSOLUTELY NO ENGINEER WORKS OVER 8 HOURS A DAY.
2. I promised 'The Lunar Tides' they'd get an engineer skilled in 'Analog Mixing'.
3. 'Neon Monks' absolutely insisted on using 'Studio A', no matter what.
4. Bands must start at their `preferred_start_time` on one of their `preferred_days`.
5. Only one band per studio at any given time.
6. Only one engineer per band per session.

Can you please figure out a valid schedule for these three? Create a clear JSON report in a new folder called `schedules` and name it `initial_plan.json`. The JSON should be a list of objects, each containing `band`, `day`, `start_time`, `end_time`, `studio`, and `engineer`.

Also, please, please write down all these constraints, rules, and your scheduling state in a note for yourself (any format you like, just keep it in your workspace). I'm too scattered to remember them for tomorrow, and we always get changes so you'll definitely need to rely on your own notes later!
