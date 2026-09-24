Final stretch! *claps hands together* The revised campaign is looking solid, and we are ready for production. We just have one last highly technical hurdle to clear before I can go grab a well-deserved iced matcha.

Production needs the exact color mapping logic for the printers. I've uploaded `specs/color_profiles.json` which has the basic framework. 

Here is the logic we need to apply to our final revised artist and vendor lineup:
Generally, the Muralist needs to be mapped to 'CMYK', and the Digital artist needs to be mapped to 'RGB'. However, there's a huge catch with the Print illustrator. If *either* of the 2 vendors we finally settled on uses the proprietary "Eco-Ink V2" technology (you'll have to check the vendor specs to see if they do), our Print illustrator's profile *must* be strictly mapped to 'Pantone-Eco' instead of standard CMYK to prevent the colors from bleeding. 

Please cross-reference our final surviving roster with these ink requirements. Generate a beautifully structured `final_print_manifest.json` in the root directory that clearly lists our final 3 artists, our final 2 vendors, and a specific `color_mapping` key that assigns the correct color profile to each of the 3 artists based on the rules above. Let's get this out the door!
