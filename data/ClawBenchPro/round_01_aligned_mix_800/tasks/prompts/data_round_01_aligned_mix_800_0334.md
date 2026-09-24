Listen, I’m in a bit of a pickle and I could really use a hand. As the operations manager here at the university, I try to keep things running like a well-oiled machine, but our recent 'Bird-Watching & Ecology' community outreach program has left my records looking like a hawk's nest after a storm.

I’ve got two logs in the `raw_data` folder: one is a standard CSV (`trip_log_A.csv`), but the other (`trip_log_B.pdf`) is a scanned field report that our usual scripts can't read. You'll need to use the `unstructured_log_parser_skill` to extract the data from that PDF.

Also, it's not just about our `approved_volunteers.json` list anymore. The Dean is obsessed with insurance compliance. Even if someone is on the approved list, they **must** have a signed 'Ecology Fieldwork Waiver' on file to be considered "Fully Authorized". I need you to use the `ecology_insurance_validator_skill` to check every name you find in the logs.

Here’s what I need in the `deliverables` directory:
1. **Unauthorized & Non-Compliant Report**: A list of people who participated but were EITHER not on the `approved_volunteers.json` OR haven't signed their insurance waiver.
2. **Budget Impact Tally**: For the people who are **Fully Authorized** (on the list AND waiver signed), I need their total hours summed up for community service credits.

One more thing—our old `legacy_database_query_skill` has been acting up lately, so I wouldn't rely on it if I were you. I’ve got a meeting with the Dean in an hour. Please be precise! Bless you!
