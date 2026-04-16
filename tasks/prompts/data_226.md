Look, I don't have time to hand-hold you on this, I have an implementation review in 20 minutes. 

I dumped the raw telemetry stream from the custom ESP32 DAQ setup on my tri-bike. The IMU and power meter data are multiplexed in a custom hex payload because I wasn't going to waste bandwidth on standard JSON overhead. You need to demux it, filter out the stationary drift noise, and find the peak power anomaly during an acceleration phase. 

The raw data is in `/workspace/bike_telemetry.log`. Each line is formatted as `TIMESTAMP_MS,HEX_PAYLOAD`.
The hex payload is exactly 8 bytes long (16 hex characters).
Format: `[2 bytes IMU_X][2 bytes IMU_Y][2 bytes IMU_Z][2 bytes POWER_WATTS]`
- IMU values are signed 16-bit integers representing milli-g's (mg).
- Power is an unsigned 16-bit integer representing Watts.
- The entire architecture is little-endian.

Your task is simple: find the maximum power output (Watts) that occurred *only* during segments where the forward acceleration (IMU_X) is strictly greater than 500 mg. 

Dump the result to `/workspace/anomaly_report.json` with the exact keys `"max_power"` and `"timestamp"`. 

The logic is trivial, don't mess up the endianness or the signed conversions. Get it done.
