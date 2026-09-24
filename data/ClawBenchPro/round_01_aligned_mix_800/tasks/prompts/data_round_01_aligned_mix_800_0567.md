Look, I don't have the time or the patience to explain this twice. I finally got my hands on the new XR-900 multi-phase photon detector, and I need to calibrate its telemetry module immediately. My last lab assistant—who I had the absolute pleasure of firing this morning—left the recent spectro-resonance logs in a catastrophic state. Because he had zero concept of basic EMF shielding or data management, the `sensor_dumps` folder is a labyrinth of fragmented garbage.

Here is what you need to fix:
1. **The ID Disconnect**: The idiot didn't log the `sample_id` in the raw data. He logged the `device_id`. You'll have to find the device registry file he hid somewhere in the `config` directory to map the devices back to their actual sample IDs.
2. **The Blackouts**: We had severe rolling blackouts last month. The facility manager dumped a text log of the power failures in `sys_logs/power_events.txt`. Any sensor reading whose timestamp falls *inclusively* within those blackout windows is completely fried. Drop them.
3. **Corrupted Junk**: Half the files in the dumps are backups, corrupted binaries, or missing headers. Only process the actual `.csv` and `.jsonl` files. For the readings themselves: if the amplitude is below zero, it's physically impossible. If the 'status' flag is anything other than exactly `OK` (he used 'ERR', 'WARN', 'OOM', etc.), the sensor was out of alignment. Ignore all of it.

I need you to crawl through that mess, filter out the noise, blackout periods, and invalid statuses, and calculate the average valid amplitude for each `sample_id`. 

Dump the final mapping of sample ID to its average amplitude into a clean file called `clean_metrics.json` inside the `workspace` directory. Round the averages to exactly 2 decimal places so my parser doesn't choke on floating-point anomalies. I don't care if you write a script or use witchcraft, just get it done. I need to get back to soldering this custom circuit board before my grant meeting tomorrow.
