Hey there, kindred spirit! 🌿 I am SO incredibly excited to cross paths with you! ✨ 

This past weekend, my amazing elementary and middle schoolers participated in our "Eco-Warriors" park cleanup! We started the morning with some barefoot grounding on the earth—it was absolute magic! 🧘‍♀️🌍 

But here's where my radiant energy turns into a tiny bit of panic... 😅 The district gave us a buggy little check-in app for the event. Instead of a nice, clean spreadsheet, it spat out hundreds of tiny, messy files scattered all over the `scans/checkins/` directory. To make matters worse, some of the kids accidentally scanned their badges using an offline terminal with a dying battery, so there are totally corrupted files in there! The app also mixed in logs from our garden club at the `School_Yard` earlier this month. I strictly only need the hours logged where the `location` is explicitly set to `EcoPark`! 

Also, for our school's community service grant (yay for sustainability funding! 🌱), I desperately need to tally the volunteer hours. Our student registry is sitting in `db/roster.csv`. I need you to calculate the total hours contributed at EcoPark, organized by grade level.

Oh, and the permission slips... My co-admin, Jill, logged all the permission slip updates into a chaotic running diary at `admin_records/slip_transactions.log`. Since parents are constantly changing their minds, kids might have multiple entries in that log. The **ONLY** thing that matters is the absolute *last* recorded status for each student in that timeline. If a student showed up at EcoPark and logged *any* time greater than zero, but their absolute final slip status in the log isn't `Signed` (like `Void`, `Pending`, or they just have no record at all), I need them on a liability list immediately!

Could you please work your analytical magic and generate a beautiful JSON report for me? Save it as `report.json` in the `final_docs/` folder. 

I need it to have exactly these two keys:
- `"hours_by_grade"`: A mapping of the grade (e.g., "5") to the total hours contributed (decimals are fine!).
- `"missing_slips_participants"`: A perfectly alphabetical list of the full names (not IDs!) of the lovely students who volunteered at EcoPark but don't have a valid final signed slip.

You are a true lifesaver! Thank you SO much for restoring balance to my universe! Have a beautifully radiant day! ✨
