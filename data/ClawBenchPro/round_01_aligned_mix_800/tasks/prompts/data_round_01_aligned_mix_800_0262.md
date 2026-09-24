*tap, tap, tap* 

Dios mío, you hear that? That's my foot tapping because I've been waiting twenty minutes for dispatch to answer the radio. I'm sitting in my cruiser, I've got my sketchbook open on the steering wheel trying to draw this busted fire hydrant to calm my nerves, but these dispatch IT systems are driving me up the wall! 

Look, I need your help. I'm supposed to be enforcing motor vehicle laws, not doing desk work. They dumped a bunch of raw text logs from the automated traffic cameras into the `dispatch` folder. Inside, there's a file with the camera readings (`speed_logs.txt`) and another file with a list of *suspected* stolen license plates (`suspect_plates.csv`). 

I don't have the patience to cross-reference this manually, and here's the catch: that CSV is just an unverified tip-line list. First, you must verify which of those suspect plates are *actually* reported stolen in the national database. The old dispatch mainframe is notoriously broken, so you might have to use our new cloud NCIC database query tools to check their status. 

Once you confirm which plates are officially "STOLEN", comb through those camera logs. 
First, tell me if any of those confirmed stolen plates passed by our cameras today. 
Second, I need to know the worst location for speeding—specifically, where the highest number of cars were going *over 65 mph*. I want to know exactly where to park my cruiser tomorrow. 

Take your findings and put them in a clean JSON file called `daily_briefing.json` inside a `reports` folder. Make sure the system can read it easily—just give me a list of the spotted stolen plates under the key `stolen_spotted`, and the name of that terrible speeding location under `worst_hotspot`. 

Get it done quickly so I can get back to patrol and make it home in time to see my kids. Move!
