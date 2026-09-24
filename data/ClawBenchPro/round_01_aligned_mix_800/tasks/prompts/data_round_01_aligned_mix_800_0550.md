Hey there. I'm Declan. 

I haven't taken my sun hat off since 5 AM and the Florida heat is already getting to me. I'm the agricultural manager for our organic crop division here, and frankly, I'd rather be out in the groves or taking my toddler on a nature walk than staring at a computer screen. But the corporate board is breathing down my neck.

Here's the situation. We're strictly organic—Green Party principles, heavy on environmental conservation. But the conventional farm next door keeps spraying synthetic pesticides, and I'm almost certain the drift blew over into our boundary plots over the weekend. They’re wiping out our beneficial insect populations and the pest index in those areas is skyrocketing. 

The problem is, our telemetry system crashed on Sunday. Instead of the nice, clean summary spreadsheets we usually get, Sunday's data got fragmented into hundreds of tiny individual files. I also know our sensors accidentally pick up data from the neighbor's conventional plots, which is just adding to the mess.

I left an urgent memo in the `communications` directory explaining our exact thresholds for what constitutes a "compromised" plot and how to filter out the neighbor's data. 

I need you to write a script to sift through all this mess. Don't try to do it by hand—there are hundreds of files. Once you calculate everything based on my memo, put the results in a new folder called `desk_drawer` in a file named `report.json`. The JSON file must contain exactly two keys:
1. `compromised_plots`: A sorted list of strings containing the IDs of our organic plots that were ruined by the drift.
2. `total_safe_yield`: An integer representing the combined yield of all our *healthy* organic plots.

Please handle this quickly and precisely so I can give the board an accurate inventory and get back outside to my family.
