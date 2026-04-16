import os

def build_env():
    base_dir = "assets/data_214"
    os.makedirs(base_dir, exist_ok=True)

    logs = """[2023-10-01 08:14:02] INFO - Machine started.
[2023-10-01 09:00:00] INFO - Processing organic cotton batch #102.
[2023-10-01 10:22:15] ERROR - Component: Spindle_A | ERROR_CODE: EW-404 | Downtime: 45 mins
[2023-10-01 11:00:00] INFO - Resumed operation.
[2023-10-01 14:05:00] INFO - Processing recycled poly-cotton blend.
[2023-10-02 09:12:11] ERROR - Component: Tension_Belt | ERROR_CODE: EW-102 | Downtime: 120 mins
[2023-10-02 11:30:00] ERROR - Component: Tension_Belt | ERROR_CODE: EW-102 | Downtime: 60 mins
[2023-10-02 14:00:00] INFO - Maintenance performed on Tension_Belt.
[2023-10-03 08:30:00] INFO - Machine started.
[2023-10-03 09:45:12] ERROR - Component: Extruder_Valve | ERROR_CODE: EW-505 | Downtime: 30 mins
[2023-10-03 13:20:00] INFO - Processing hemp fibers.
[2023-10-04 10:10:00] ERROR - Component: Tension_Belt | ERROR_CODE: EW-103 | Downtime: 40 mins
[2023-10-04 15:40:00] ERROR - Component: Spindle_A | ERROR_CODE: EW-404 | Downtime: 15 mins
[2023-10-05 08:00:00] INFO - System update applied to EcoWeave 3000.
[2023-10-05 11:11:11] ERROR - Component: Tension_Belt | ERROR_CODE: EW-102 | Downtime: 90 mins
[2023-10-05 16:00:00] INFO - Shutdown sequence initiated.
"""
    with open(os.path.join(base_dir, "machine_logs.txt"), "w", encoding="utf-8") as f:
        f.write(logs)

    template = """# EcoWeave 3000 Maintenance Summary

## Performance Metrics
- **Total Downtime (minutes):** [INSERT TOTAL DOWNTIME HERE]
- **Most Frequent Failing Component:** [INSERT COMPONENT NAME HERE]

## Diagnostic Information
- **Unique Error Codes:** [INSERT COMMA-SEPARATED LIST OF UNIQUE ERROR CODES HERE]

*Report generated for sustainable manufacturing compliance.*
"""
    with open(os.path.join(base_dir, "template.md"), "w", encoding="utf-8") as f:
        f.write(template)

if __name__ == "__main__":
    build_env()
