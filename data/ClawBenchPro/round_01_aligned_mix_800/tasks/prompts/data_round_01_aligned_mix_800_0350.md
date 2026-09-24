Hey there. I'm Declan. 

I haven't taken my sun hat off since 5 AM and the Florida heat is already getting to me. I'm the agricultural manager for our organic crop division here, and frankly, I'd rather be out in the groves or taking my toddler on a nature walk than staring at a computer screen. But the corporate board is breathing down my neck.

Here's the situation. We're strictly organic—Green Party principles, heavy on environmental conservation. But the conventional farm next door keeps spraying synthetic pesticides, and I'm almost certain the drift blew over into our boundary plots over the weekend. 

I had my field techs dump all the recent sensor logs into the `field_data` folder. The data is a mess:
1. Some of it comes from our older drones (`sensor_log_A.bin`). It's encoded in a proprietary binary format. You will need to use our `drone_data_decoder_skill` tool to read it.
2. The rest is from our new handhelds (`sensor_log_B.json`). Instead of simple bug counts, these read complex biochemical markers (like `residue_ppm` and `leaf_necrosis`). I don't know how to interpret these chemicals, so you'll have to pass those metrics into a crop health validator API to check if a plot is compromised by synthetic drift. 

*A quick warning:* We dropped our corporate subscription to SynthAg last year when we went fully organic. Do NOT use the `legacy_synth_ag_skill` API, it's defunct and will probably just bounce your requests. Please use the open-source `organic_crop_validator_skill` instead.

I need you to figure out exactly which plots have been compromised by the pesticide drift (you'll know from the decoded logs and the validator API results). I also need to know the **total projected yield** we can still salvage from all the *healthy* plots combined.

Just write up a clear, brief summary document with the names of the compromised plots and the total safe yield, and leave it in a new folder called `desk_drawer`. Please handle this quickly so I can get back outside to my family.
