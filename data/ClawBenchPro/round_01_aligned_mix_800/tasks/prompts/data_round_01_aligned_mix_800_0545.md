Hey there! *waves hands excitedly but also visibly shaking from caffeine* 

I’m in a massive bind! The community board meeting is tonight, and my record-keeping has been... well, a bit too "free-spirited". I dumped all the recent sign-up sheets, corporate pledges, and IT system dumps into the `campaign_mess` directory. It’s a total disaster zone.

Here’s the thing: we had some corporate sponsors pledge money for the "Park Cleanup" initiative, but I swear some of those big businesses are trying to pull a fast one and haven't actually paid up yet. I need you to dig through those files and figure out exactly which businesses promised us funds but are still labeled as "PENDING". Corporate accountability, right?! 

Also, I need to know the total, exact number of HOURS our amazing volunteers actually put into the Park Cleanup specifically. 

A few things to keep in mind so you don't go insane:
- IT upgraded our system last month, so everything uses these weird internal Project Codes now. I think I left an IT memo in there somewhere that explains which code belongs to the Park Cleanup. 
- Pledges are scattered in these weird quarterly batch files. They only list corporate IDs, not the actual business names! The names are in some registry file.
- The volunteer timesheets are totally fragmented by week. And get this: the new system tracks time in *minutes*, but I need the final total in *hours*. Oh, and please only count the timesheets marked as "APPROVED"! Some people tried to log hours for just standing around drinking smoothies (those are marked "REJECTED" or "DRAFT").

Could you please put together a nice, neat JSON summary report? Create a new folder called `deliverables`, and put a file named `report.json` inside it. I need it to have exactly two keys:
1. `flaky_businesses`: A list of the actual business names (strings) that are still PENDING for the Park Cleanup.
2. `total_park_cleanup_hours`: The total approved volunteer hours (a float number) for the Park Cleanup.

You're a lifesaver! Keep fighting the good fight!
