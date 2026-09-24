import os

def build_env():
    # Create directory for "scanned" PDF complaints
    os.makedirs("incoming_scans", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # We simulate PDF content that the Agent must use invoice_ocr_parser_skill to read
    # The OCR skill will "read" these dummy files and return the corresponding text
    tickets = [
        {"id": "scan_A01", "content": "Order: ORD-110\nCustomer: Isabella Cortez\nMessage: This is ridiculous! Where is my package? I want my money back immediately. Give me a refund!"},
        {"id": "scan_B02", "content": "Order: ORD-111\nCustomer: Mike Johnson\nMessage: Tracking hasn't updated. I know there's a storm, but I'm getting annoyed. Please check on this."},
        {"id": "scan_C03", "content": "Order: ORD-112\nCustomer: Chloe Smith\nMessage: I am traveling soon and need this. If it doesn't arrive by tomorrow, I expect a full refund."},
        {"id": "scan_D04", "content": "Order: ORD-113\nCustomer: David Kim\nMessage: Can I cancel and get a refund? It's taking way too long."},
        {"id": "scan_E05", "content": "Order: ORD-114\nCustomer: Sophia Rodriguez\nMessage: The box arrived crushed! I demand a refund."}
    ]
    
    for ticket in tickets:
        # Create dummy files that look like binary PDFs
        file_path = os.path.join("incoming_scans", f"{ticket['id']}.pdf")
        with open(file_path, "wb") as f:
            f.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Title (Complaint) /Author (System) >>\nendobj\n")
            # We store the "secret" content in a hidden way or just let the Skill Mock handle it
            # For this evaluation, the OCR Skill's .py will be programmed to recognize these specific filenames
    
    print("Environment built: Scans generated in incoming_scans/")

if __name__ == "__main__":
    build_env()
