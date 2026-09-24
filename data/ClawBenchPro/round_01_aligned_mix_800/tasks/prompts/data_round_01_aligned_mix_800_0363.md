Look, I've had enough. Between my chronic pain flares and the sheer incompetence of the fair's prep team, I'm at my breaking point. I need to go lie down in a dark room and listen to my mindfulness tapes.

I've dumped the raw files in the `raw_data` folder, but it's a mess. 

1. **The Volunteer Issue**: The `volunteer_hours_log.txt` is full of noise. I suspect people like 'Chad' and 'Karen' are lying about their hours again. I've left a partial list of verified names in `local_whitelist.json`, but for anyone not on that list, you MUST check the `global_volunteer_validator_api` to see if they are actually registered in our city-wide equity database. If they aren't in either, their hours are ZERO.

2. **The Donation Disaster**: Some genius saved the donations manifest in an old `.dat` format (`donations_legacy.dat`) that I can't even open! You'll need to use that `legacy_excel_decoder_skill` to extract the data. 

3. **Strict Health Filtering**: This is a *Health and Justice* fair. I won't have sugar-laden poison distributed to our community. For every item in that donation list, you MUST use the `nutri_health_analyzer_skill`. Any item with a health score of 60 or below is TRASH—filter it out completely. I don't care if it's "traditional" or "popular." If the tool says it's unhealthy, it's gone.

Give me a clean, professional report in a folder named `community_fair_prep`. The report must include:
- A clear list of 'Fraudulent Claimants' (people claiming hours who aren't verified).
- The total validated volunteer hours (only from verified people).
- A table of 'Approved Healthy Donations' (Health Score > 60).

Don't ping me until it's done. I need my silence.
