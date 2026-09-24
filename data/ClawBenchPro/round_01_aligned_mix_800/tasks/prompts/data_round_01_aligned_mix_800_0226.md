Hey. *waves hand dismissively* I'm trying to get my weekend woodworking project started—building a new dining table—but the mill's apprentice is a disaster. He's dumped our inventory across two different files in the `inventory_logs` folder.

One is a standard CSV, but instead of writing "Usable", he used these industry defect codes (like 'KN-1', 'CR-5'). I don't have time to remember which ones are okay for furniture—you'll need to use the `lumber_grading_analyzer_skill` to check if a board is actually "Furniture Grade".

The other log is a scanned receipt from the old mill (`mill_receipt_scan.pdf`). You'll need to use the `ocr_blueprint_parser_skill` to read what's in there. I'm only interested in 'White Oak'. 

Find all the 'White Oak' boards that are 'Furniture Grade' (skip anything the analyzer flags as unusable), and figure out the total board feet. 
Formula: (Thickness * Width * Length) / 144. (All units are in inches).

Generate a clean JSON document named `usable_oak_report.json` in the `project_planning` folder. It must show the total usable board feet and a list of those specific boards. No fluff, just get it done.
