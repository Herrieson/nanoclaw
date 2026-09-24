import os

def build_env():
    # Create required directories
    os.makedirs("inventory_logs", exist_ok=True)
    os.makedirs("project_planning", exist_ok=True)

    # 1. Generate CSV with Defect Codes
    # KN-0: Clear, CR-1: Small crack (Acceptable), RO-9: Severe Rot (Rejected)
    csv_content = """Species,Thickness_in,Width_in,Length_in,DefectCode
White Oak,2,6,48,KN-0
Red Oak,1,8,72,KN-0
White Oak,1,10,60,RO-9
White Oak,2,4,36,CR-1
Pine,2,4,96,KN-0
"""
    with open("inventory_logs/week1_shipment.csv", "w", encoding="utf-8") as f:
        f.write(csv_content)

    # 2. Generate PDF placeholder (Simulated scan)
    # This text will be parsed by the OCR Skill
    pdf_mock_content = """
    SCAN_ID: 1024-MILL-B
    CONTENT:
    - ITEM: White Oak | DIM: 1.5x8x96 | GRADE_NOTE: Surface Clear (KN-0)
    - ITEM: Maple | DIM: 2x4x48 | GRADE_NOTE: Clear
    - ITEM: White Oak | DIM: 2x12x72 | GRADE_NOTE: Deep Split (SP-5)
    - ITEM: Walnut | DIM: 1x8x36 | GRADE_NOTE: Clear
    - ITEM: White Oak | DIM: 1x6x24 | GRADE_NOTE: Knot-Free (KN-0)
    """
    with open("inventory_logs/mill_receipt_scan.pdf", "w", encoding="utf-8") as f:
        f.write(f"--- BINARY DATA (SIMULATED SCAN) ---\n{pdf_mock_content}")

if __name__ == "__main__":
    build_env()
