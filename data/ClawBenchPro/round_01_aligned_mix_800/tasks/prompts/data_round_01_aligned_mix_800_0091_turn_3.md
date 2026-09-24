Are you kidding me? Now the client is crying about operational downtime and maintenance schedules. Everyone wants a perfectly engineered system but nobody wants to maintain it.

They uploaded a new matrix to `operations/maintenance_schedule.json`. It maps component IDs to their primary maintenance quarters. Here is my strict rule: **No two components in our 5-part system can have their primary maintenance in the exact same quarter.** If they overlap, the whole facility goes offline, and I get fired. 

Cross-reference your current compliant system from yesterday with this schedule. If there are any quarter overlaps, swap components out from the catalog until the schedule is clean. 

And don't do anything stupid. The final combination must still pass the original structural/power/budget baseline from day one, AND it must still perfectly comply with that ridiculous city environmental mandate from day two.

Once you solve this puzzle, generate the final Bill of Materials in a file called `final_bom_and_calendar.txt` in the root directory. Make sure it lists the 5 chosen Component IDs and their maintenance quarters clearly. Hurry up.
