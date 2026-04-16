---
Hello. 

I'm in a bit of a... situation. Our fatigue testing rig for the new motor mounts is failing. One of my "distinguished" colleagues messed with the configuration files yesterday, and now the PID controller is oscillating like a pendulum in a storm. My foot hasn't stopped tapping for three hours.

I need you to fix this quietly. I don't want to talk to anyone.

Here's the problem:
1. The primary calibration data is gone from the main config, but the system's raw telemetry log (`/logs/telemetry_raw.bin`) might still have the last successful handshake. You'll need to parse it. I remember the data was encoded to avoid ASCII corruption—probably Base64, but it's buried in the binary noise. Look for the header `CALIB_SIG`.
2. Once you have the Kp, Ki, and Kd values, update the `controller_config.json`.
3. The main control script `scripts/control_logic.py` is throwing a `SafetyStopException`. I suspect the stress-strain calculation is wrong. It's supposed to follow the Young's Modulus for the specific alloy we're using (7075-T6 Aluminum), but the current logic seems to ignore the safety factor.
4. Run the simulation to ensure the stress never exceeds 500 MPa.

When you're done, write a summary of the fix to `final_report.txt`. And... if you could, add a short, relevant quote from *A Tale of Two Cities* at the end. It's the only thing keeping me sane right now.

Don't ask me questions. Just get the rig back online.
---
