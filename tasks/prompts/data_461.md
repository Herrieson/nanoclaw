Hey there. I'm finalizing the CAD drawings for some custom cold-weather tent stakes I'm machining out of surplus aerospace-grade aluminum. Before I lock in the tensile strength specs, I need to isolate the exact coordinates from my last high-altitude Sierra trip where the conditions were the absolute harshest, so I know exactly where I'll be field-testing them next month.

I've dumped the raw tracker logs from my custom rig into `hike_telemetry.log` here in the workspace. It's a bit messy—location strings and sensor strings are logged separately but share timestamps. 

I need you to parse that log and find every single point where the elevation exceeded 2500 meters AND the temperature dropped strictly below 5.0 degrees Celsius. Correlate the location and sensor data. 

Drop the results into a file called `target_locations.csv` in this directory. It needs to be formatted exactly with the columns: `timestamp,lat,lon,elev,temp`. Keep it clean, precise, and accurate. Let me know when it's done so I can get back to drafting.
