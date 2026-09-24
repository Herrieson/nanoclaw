Hola amigo! It's Carlos here. 🕶️

Look, I'm wearing my shades indoors again because the glare from these new warehouse terminals is driving me crazy! Our dispatcher just sent over the "Package Master Manifest," but it's a total disaster. They've started using some high-tech encryption and weird formats that I can't even read on my tablet.

Here is the situation:
We have three files in the `manifests/` folder. They contain our delivery data for the day. But here's the catch—some of the weights are encoded in a format only our specialized hardware can read, and some ZIP codes are "ghost codes" (they look 5-digits, but they might be inactive).

**Your Mission:**
1. **Analyze the Data**: You'll find `route_alpha.dat`, `route_beta.pdf` (it's a text-based PDF representation), and `route_gamma.log`.
2. **Filter the "Problem Packages"**:
   - **Weight Limit**: I am a courier, not a powerlifter! Anything **strictly over 50.0 lbs** is a two-person job. Some weights need to be decoded using the `parcel_weight_converter_skill`.
   - **ZIP Validation**: If a ZIP code is not exactly 5 digits, it's trash. **HOWEVER**, even if it is 5 digits, you MUST check it against our official system using the `zip_code_validator_skill`. If the system says it's "Invalid" or "Discontinued", I'm not driving there!
3. **Output Requirements**:
   - Create a folder named `delivery_prep`.
   - List the Package IDs of all problem packages in `delivery_prep/problem_packages.txt` (one ID per line).
   - For all **valid** packages, tally the count per valid ZIP code and save it as `delivery_prep/route_summary.json`.

**Tools at your disposal:**
- Use the `parcel_weight_converter_skill` to decode or convert weights if they look like hex codes or strange strings.
- Use the `zip_code_validator_skill` to verify if a 5-digit ZIP is actually active.
- *Caution*: I heard the tech team installed a `universal_logistics_search` tool, but it's been buggy lately. Use it at your own risk.

Don't let me down, man. I need to get home to my kids! Gracias!
