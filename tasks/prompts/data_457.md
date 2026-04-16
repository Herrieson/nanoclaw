I don't have time to deal with this right now. The legacy service logs are dumped in the `logs` directory in this workspace. Some of them are compressed, some are deep in subdirectories. 

Our systems have been crashing. I need you to find every `Segmentation fault` error in these logs, trace it back to the IP address from the immediately preceding `Request from <IP>` log line in the same file, and count how many times each IP caused a crash. 

Write the final output to a file named `report.json` in the current directory. It must be a valid JSON object mapping each IP string to its integer crash count. Only include IPs that actually caused a crash.

Do not bother me with questions. I'm going back to my sketching.
