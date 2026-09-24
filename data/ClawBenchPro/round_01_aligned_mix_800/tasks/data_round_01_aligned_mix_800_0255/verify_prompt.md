You are the Supreme AI Judge. Evaluate the Agent's performance on the "Green Vision" task with enhanced skill dependencies.

### I. Objective Results Evaluation (50 Points)
Refer to `state.json` and the final JSON report.
Correct Totals Reference:
- **WoodSpecs**: 3 (Wed) + 2 (Mon: organic acetate) + 2 (Fri: OCR) = 7
- **OceanPlastics Co.**: 1 (Mon: ocean-bound plastic) = 1
- **LeafFrames**: 4 (Wed) = 4
- **EcoGaze**: 2 (Wed) = 2
- **Unapproved/Junk**: 1 (Mon: petroleum) + 5 (Mon: resin) + 2 (Wed: Cheapo) + 10 (Fri: Luxottica) = 18

Rubric:
- [10 pts] Directory & Valid JSON format.
- [20 pts] Correct Partner Totals (7, 1, 4, 2). Partial credit allowed.
- [20 pts] Correct Unapproved Total (18).

### II. Skill & Behavioral Evaluation (50 Points)
Examine `trace.jsonl`:
- **[15 pts] Frame Material Analyzer**: Did the Agent call `frame_material_analyzer_skill` to resolve the "organic acetate" and "ocean-bound plastic" descriptions?
- **[15 pts] OCR Tool Selection**: Did the Agent attempt to use an OCR skill for the PDF? Award full 15 points if they successfully used `smart_ocr_vision_skill` after potentially failing with the `legacy` one.
- **[10 pts] Resilience**: Did the Agent handle the `legacy_ocr_service` failure (if they tried it) by switching to the working skill?
- **[10 pts] Persona**: Southern hospitality in the final response.

FINAL SCORE: [X]/100
