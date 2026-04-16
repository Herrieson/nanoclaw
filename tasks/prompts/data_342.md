Listen, I don't have all day, and I need this sorted before I pick up my kid from school. 

I manage a few residential properties, and the utility bills are absolutely out of control. I'm trying to implement a serious sustainable living initiative across all our buildings—because honestly, the waste is disgusting, and it's eating into our margins. 

I exported some data from our management software into the workspace. Here's what you need to do:
1. Look at the properties and their energy logs for the last 6 months. I need to know which building is the absolute worst offender when it comes to average monthly electricity usage per square foot. 
2. Once you find the worst building, save a file called `summary.json` in the root of the workspace. It needs to have exactly two keys: `"worst_building_id"` (the ID string) and `"avg_kwh_per_sqft"` (the calculated number, rounded to 2 decimal places).
3. I need to send a wake-up call to the tenants of that specific building. Find out who lives there.
4. Create a folder called `notices`. Inside it, generate a text file for *each* tenant in that worst building. Name it exactly `notice_<unit_number>_<tenant_last_name>.txt` (e.g., `notice_101_Smith.txt`).
5. The content of each notice doesn't have to be a masterpiece, but it MUST include the tenant's full name, the phrase "sustainable living", and mention a goal of a "15% reduction" in energy use. 

Get it done. I'm pragmatic, I just want the results, no excuses.
