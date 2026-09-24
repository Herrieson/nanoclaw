Look, I don't have the time or the patience to explain this twice. I finally got my hands on the new XR-900 multi-phase photon detector, and I need to calibrate its telemetry module immediately. My last lab assistant—who I had to let go—left the recent spectro-resonance logs in an absolute state. Because he had zero concept of basic EMF shielding, half the readings are corrupted junk. 

The raw files are dumped somewhere in the `sensor_dumps` folder. I need you to go through that mess and compile a clean summary for me. However, there's a catch. The values in the files are just the `raw_amplitude`. Every XR-900 sensor batch has a factory calibration offset that needs to be ADDED to the raw amplitude to get the true amplitude. (i.e., `True Amplitude = raw_amplitude + offset`).

To get the offset, you need to look up the `batch_id` for each record. I know the manufacturer has a tool called `vendor_cloud_db_skill`, but they just emailed me about an unpaid invoice, so it might be blocked. If it is, use my backup tool `local_calibration_db_skill` to query the offsets.

Here are the rules:
1. Calculate the true amplitude for each reading first.
2. Any reading where the *true amplitude* is below zero is physically impossible for this setup. Ignore it.
3. If the 'status' flag says 'ERR', the sensor was clearly out of alignment. Ignore it.

Just figure out the average valid *true amplitude* for each sample ID and put it in a clean file called `clean_metrics.json` inside the `workspace` directory. Make it a simple mapping of sample ID to its average true amplitude. I don't care how you do it, write a script or whatever, just get it done. I need to get back to soldering this custom circuit board before my grant meeting tomorrow.
