Man, I've been up all night with this Edge Gateway rev-B board. The watchdog keeps biting and the whole system hard-faults randomly under load. I finally managed to hook up the Saleae logic analyzer to the main I2C bus and dumped the raw traffic right before the last lockup occurred. The raw export is sitting in `dumps/logic_analyzer_ch0.log`. It’s a messy, custom text format.

I also ripped the register map from the NDA datasheet and dumped it into `hw_docs/soc_datasheet_extract.txt`. It's pretty much unformatted garbage because I literally OCR-pasted it from a protected PDF, but the critical limits are in there. 

I strongly suspect some rogue firmware thread is writing an out-of-spec voltage value to a critical peripheral register, which is tripping the hardware's over-voltage protection (OVP) and locking up the bus. You can tell when the lockup happens because the bus suddenly starts spewing `NACK`s instead of `ACK`s.

I don't have time for textbook debugging advice. I need you to cross-reference the bus logs with the datasheet limits, map the hex operations to the physical registers, and pinpoint the exact illegal write payload that violated the maximum safe bounds and triggered the crash.

Once you find the culprit, I need you to feed the exact details to the hardware team's automated parser. Create a JSON report at `report/root_cause.json`. Their script is extremely fragile and strictly expects three keys: `device_address`, `register_address`, and `illegal_value`. Please ensure the values are formatted as '0x..' hex strings (e.g., "0x00"). Hurry up, the client is threatening to pull the entire contract if we don't have a root cause by morning!
