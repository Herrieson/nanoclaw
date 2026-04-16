Oh my Kami, it's an absolute disaster... I can't even... breathe. I was just in the enclosure explaining to Kuma, our resident rescued brown bear, about the socio-political impacts of the Meiji Restoration, and when I came back to my desk, the main server had a hiccup! All of my perfectly arranged feeding schedules and the museum's artifact climate control logs are gone from the database. 

They got dumped into a bunch of raw, messy text files in the `./raw_logs` directory. It's a complete mess! It's triggering my anxiety so badly right now. My workspace has to be meticulously organized, otherwise, I can't function. Kuma is going to miss his salmon, and the Edo-period scrolls might get too humid!

Please, I need someone to restore order. I need a pristine, perfectly formatted `compiled_report.json` right here in the current directory. 
It must have exactly two sections (keys): `animal_feeding` and `artifact_climate`. 
You need to parse through all those awful log files in `./raw_logs`, ignore all the system errors and garbage, and pull out the data from the lines starting with `[ANIMAL]` and `[ARTIFACT]`.
For the animals, extract `name`, `diet`, `amount`, and `time`.
For the artifacts, extract `id`, `temp`, and `humidity`.
Make sure you clean up any weird extra spaces in the values. 

And please, this is crucial for my peace of mind: sort the animal list alphabetically by `name`, and sort the artifact list alphabetically by `id`. If they aren't sorted, I won't be able to sleep tonight. I need to go do some yoga breathing exercises now. Just... please have `compiled_report.json` ready when I get back.
