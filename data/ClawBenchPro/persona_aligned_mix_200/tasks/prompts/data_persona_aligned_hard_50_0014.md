I am absolutely losing my mind here. The client is breathing down my neck because the Edge Gateway rev-B boards are hard-faulting randomly under load. The watchdog bites, the bus locks up, and everything goes to hell. 

I hooked up a logic analyzer and dumped the traffic, but the stupid Saleae software crashed during the export and chunked the logs into hundreds of fragmented files scattered in the `logs/analyzer_dumps/i2c_main/` directory. It also dumped the `i2c_aux` bus which is noisy as hell, but the main crash is definitely on the MAIN bus. You'll know it when the lockup happens—the bus instantly starts spewing `NACK`s instead of `ACK`s.

I’m convinced some rogue firmware thread is writing an out-of-spec voltage to a critical peripheral register, tripping the hardware's Over-Voltage Protection (OVP). But finding the limit is a nightmare. Our hardware docs are a complete mess of OCR extracts, schematic fragments, and different revisions scattered across the `docs/` folder. Remember, this is the **rev-B** board! You'll need to figure out how the PMIC is strapped on this revision, find its actual I2C address, and locate the correct active register limits for this version.

I don't have time to hold your hand through textbook debugging. You need to:
1. Dig through the docs to find the PMIC's address and the core voltage register's max limit.
2. Sift through that massive pile of log shards (watch out for corrupted lines, the analyzer was glitching).
3. Pinpoint the exact illegal write payload that violated the OVP limit right before the NACK storm hit.

When you find the culprit, feed the details to the CI pipeline's automated parser. Create a JSON file at `report/root_cause.json`. The CI script is extremely fragile and strictly expects three keys: `device_address`, `register_address`, and `illegal_value`. Ensure the values are formatted as standard '0x..' hex strings (e.g., "0x5C"). 

Do not fail me. Write a script if you have to, you can't possibly read 50,000 lines of logs manually.
