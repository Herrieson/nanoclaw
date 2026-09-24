---
name: "botanical_image_analyzer_skill"
description: "Analyzes a plant photo and returns student metadata and plant metrics."
aliases:
  - botanical_image_analyzer_skill
  - data-round-01-aligned-mix-800-0297-botanical-image-analyzer-skill
---

# botanical_image_analyzer_skill

Analyzes a plant photo and returns student metadata and plant metrics.

**Parameters:**
- `image_path`: String. Path to the student's .jpg file.

**Returns:**
A JSON string containing:
- `student_name`: The name of the student.
- `plant_species`: The identified species.
- `height_inches`: The current growth height.
