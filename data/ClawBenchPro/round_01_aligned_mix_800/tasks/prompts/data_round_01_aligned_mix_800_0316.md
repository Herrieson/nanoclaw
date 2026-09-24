*pauses, letting out a heavy sigh and waving her hands in a slightly exasperated, frantic manner* 

Oh, goodness, hello! I am so incredibly relieved you're here. Between running the optometry clinic and trying to manage this community sustainability drive, my head is absolutely spinning!

We held an eyewear recycling event yesterday—collecting old glasses to either refurbish or scrap for materials. But the documentation is a disaster! 

First, I found some of the logs are in `raw_donations`, but one of the batches (`batch_02.pdf`) is a scanned PDF that I can't even read! I've installed a `handwritten_log_parser_skill` in your system which should help you extract data from such files.

Second, the `volunteers.txt` I have here is horribly outdated—it only has a few names. You **must** verify the real identity of every person in the logs using our `internal_staff_db_query_skill`. Don't trust the local text file! And please, ignore anyone who isn't a verified official volunteer.

Third, some entries in the logs have the condition marked as "TBD". For those, you'll need to use the `optical_frame_analyzer_skill` to determine if they are `Usable` or `Scrap` based on the item description.

Could you please calculate the total number of glasses marked as usable and scrap? Then, compile this into a neat little file called `final_report.json` in the `deliverables` folder. I need the usable count, the scrap count, and the final list of verified volunteers who actually processed at least one item. 

The community board meeting is tonight! Please hurry!
