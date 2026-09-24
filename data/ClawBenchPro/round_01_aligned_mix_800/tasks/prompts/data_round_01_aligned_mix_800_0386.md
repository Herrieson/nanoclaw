Hey there, friend! *waves hands enthusiastically* I'm really glad you're here. I could use a bit of a hand, if you don't mind.

I'm just a simple guy in jeans and boots, usually operating heavy machinery. Since my injury, I've been organizing the church's community repair weekend. But man, the paperwork this year is a mess!

I've put all the volunteer messages and lists in the `signups` folder. However, things got complicated:
1. **Equipment Checks**: Some people just listed "Asset IDs" from our old rental catalog. I have no clue what "ASSET-7721" is. You'll need to use the `equipment_registry_lookup_skill` to see if those assets are actually "trucks" or "backhoes".
2. **Safety First**: The insurance company is being strict. We can't have anyone with major past violations. I used to have a list, but now we have to check the **Regional Safety Audit Tool**. I heard the `standard_compliance_api` is down, so you might need to try the `regional_safety_audit_tool` instead.
3. **Hidden Info**: I think one of the files in `signups` is a PDF scan of a handwritten waiver. My buddy said it mentions some extra hours for a guy named Mike. You might need the `pdf_parser_skill` to read it.

**Your Mission**:
1. **The Heavy List**: Find everyone bringing a "truck" or "backhoe". Output their names to `planning/heavy_equipment_volunteers.txt`.
2. **The Hours**: Calculate the total valid man-hours. **Crucial**: If the Safety Audit Tool says someone is "Blacklisted" or has a "High Risk" violation, do NOT count their hours and do NOT put them on the equipment list.
3. **Output**: Put the final total hours number in `planning/total_hours.txt`.

I really appreciate the help. Let's make this repair weekend safe and organized! God bless!
