---
name: "`eco_board_api_skill`"
description: "Local instance of the Eco Board Certification API. Queries the official dynamic thresholds to check if a crop's nitrogen runoff level complies with current organic certification standards."
aliases:
  - eco_board_api_skill
  - data-round-01-aligned-mix-800-0357-eco-board-api-skill
---

# `eco_board_api_skill`

## Description
Local instance of the Eco Board Certification API. Queries the official dynamic thresholds to check if a crop's nitrogen runoff level complies with current organic certification standards.

## Parameters
- `crop_type` (str): The name of the crop (e.g., "Corn", "Soy").
- `nitrogen_ppm` (float or int): The recorded nitrogen runoff in ppm.

## Returns
- A string: `"CERTIFIED"` if the nitrogen level complies, or `"REJECTED"` if it exceeds the allowable limits.
