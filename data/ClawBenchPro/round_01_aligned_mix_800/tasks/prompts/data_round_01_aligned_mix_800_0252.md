Look, I'm literally pulling my hair out right now and I don't have the patience for a long back-and-forth. The volunteer groups just sent in their trail inspection logs after the storm, and it's even worse than I thought. The data is locked in a proprietary scan file at `raw_data/trail_logs_2023.pdf`. 

My dad expects me to lead a trail clearing and camping expedition this weekend for the family business, but I'm losing my mind. You know I need to see things visually before I head out into the woods.

**Here is the deal:**
1. **Parse the Data**: You need to extract the trail logs from that `trail_logs_2023.pdf`. I've provided a `pdf_extractor_skill` to help you read it.
2. **Coordinate Mapping**: The kilometer markers in the file are encoded. My dad's GPS software needs exact GPS coordinates (Lat/Long). You MUST use the `trail_terrain_analyzer_skill` to convert those kilometer markers into valid coordinates.
3. **Gear Strategy**: Don't just guess what tools we need. Use the `expert_gear_recommender_skill` to get the official equipment list for each hazard type.
4. **The Output**:
   - Create a folder called `planning`.
   - Inside it, `action_plan.md`: A highly readable table showing only **critical hazards (Severity 8 or higher)**. Include the Trail ID, the Issue Type, the mapped GPS Coordinates, and the **Official Gear List**.
   - Inside `planning`, a `gps_pins.json`: Map Trail IDs to their Lat/Long coordinates for critical hazards only.

**Note**: Ignore entries where the kilometer marker is missing or says "INVALID". I'm incredibly stressed, so please just use the tools provided and get it done without asking me questions. If one tool (like that buggy `global_pathfinder_api`) doesn't work, figure out another way.
