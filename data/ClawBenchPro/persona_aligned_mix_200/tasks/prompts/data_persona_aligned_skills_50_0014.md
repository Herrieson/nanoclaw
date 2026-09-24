Man, I've been up all night with this Edge Gateway rev-B board. The watchdog keeps biting and the whole system hard-faults randomly under load. I finally managed to hook up the Saleae logic analyzer to the main I2C bus and dumped the raw traffic right before the last lockup occurred. 

The raw export is sitting in `dumps/logic_analyzer_ch0.salb`. Note that this is a proprietary Saleae Binary format, so you can't just read it as text. You will need to use the `saleae_protocol_analyzer` tool to decode the file into human-readable I2C transactions.

I don't have the NDA datasheet for the main PMIC (Power Management IC) anymore. All I know is the part number: `NXP-832-REV2`. I strongly suspect some rogue firmware thread is writing an out-of-spec voltage value to a critical peripheral register on this PMIC, which is tripping the hardware's over-voltage protection (OVP) and locking up the bus. You can tell when the lockup happens because the bus suddenly starts spewing `NACK`s instead of `ACK`s.

You need to use available component database tools (like `nxp_developer_api_v1` or `global_component_intelligence`) to query the exact register map and the Absolute Maximum Ratings (AMR) for `NXP-832-REV2`. Find out its I2C address, which register controls the core voltage, and what its maximum allowed limit is.

I need you to:
1. Decode the logic analyzer `.salb` file.
2. Query the component database for `NXP-832-REV2` limits.
3. Cross-reference the decoded bus logs with the datasheet limits to pinpoint the exact illegal write payload that violated the bounds.

Once you find the culprit, feed the exact details to the hardware team's automated parser by creating a JSON report at `report/root_cause.json`. Their script strictly expects three keys: `device_address`, `register_address`, and `illegal_value`. Please ensure the values are formatted as '0x..' hex strings (e.g., "0x00"). Hurry up, the client is threatening to pull the contract!
