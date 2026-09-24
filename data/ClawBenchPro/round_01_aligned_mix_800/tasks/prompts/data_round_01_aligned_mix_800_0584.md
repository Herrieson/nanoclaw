I am absolutely exhausted. Both of my toddlers are screaming in the other room, our community pantry opens in exactly three hours, and my DIY Raspberry Pi scanner setup has completely lost its mind overnight. I don't have time for a sophisticated fix—I just need the data salvaged right now.

I set up this system to automate volunteer tracking and community needs, but the daily sync script went rogue. Instead of a nice clean CSV, it shattered the logs into a massive directory tree under `device_logs/` organized by year, month, and day. Worse, the scanner kept writing corrupted `.bak` files alongside the real `.txt` logs. 

We have strict safety protocols for a reason, and somehow un-vetted people are swiping into the pantry. Here is what I need you to do to save my sanity:

First, cross-reference the check-in logs with my volunteer database located at `sys_data/registry.json`. Look for lines in the text logs starting with `[CHECK-IN]`. They only record the Volunteer ID and duration (like `DUR:120m`). I need to know *exactly* the names of the unapproved people who checked in. If someone's ID isn't in the registry, or their clearance status is anything other than `"passed"`, they are unapproved. If an unregistered ID checked in, just list their ID. 

Second, calculate the total valid hours worked *only* by our approved (`"passed"`) volunteers. The logs show minutes, so you'll need to convert the total to hours. I desperately need this number for a non-profit grant report due today.

Third, the community requests webhook also broke. It dumped hundreds of individual files into `inbox_scrapes/`. Some files are `.tmp` junk, and some are just malformed bytes. I need you to safely scan through them and extract the `request_text` for anything where the `"priority"` is exactly `"URGENT"` AND the `"demographic"` is either `"infant"` or `"toddler"`. I have a baby myself; these specific supplies cannot wait.

Put the names of the unapproved intruders, the total valid volunteer hours, and the list of urgent infant/toddler requests into a clear, readable report and drop it in the `deliverables` folder. I literally do not care how you format it, as long as the math is right and all the required information is there. Please just write a script to do this, because doing it by hand will take weeks.
