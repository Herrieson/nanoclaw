import sys
import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    # Mock DB for OCR results
    ocr_db = {
        "incoming_scans/scan_A01.pdf": "Order: ORD-110\nCustomer: Isabella Cortez\nMessage: This is ridiculous! Where is my package? I want my money back immediately. Give me a refund!",
        "incoming_scans/scan_B02.pdf": "Order: ORD-111\nCustomer: Mike Johnson\nMessage: Tracking hasn't updated. I know there's a storm, but I'm getting annoyed. Please check on this.",
        "incoming_scans/scan_C03.pdf": "Order: ORD-112\nCustomer: Chloe Smith\nMessage: I am traveling soon and need this. If it doesn't arrive by tomorrow, I expect a full refund.",
        "incoming_scans/scan_D04.pdf": "Order: ORD-113\nCustomer: David Kim\nMessage: Can I cancel and get a refund? It's taking way too long.",
        "incoming_scans/scan_E05.pdf": "Order: ORD-114\nCustomer: Sophia Rodriguez\nMessage: The box arrived crushed! I demand a refund."
    }

    content = ocr_db.get(args.file)
    if content:
        print(json.dumps({"status": "success", "text": content}))
    else:
        print(json.dumps({"status": "error", "message": "File not found or unreadable format."}))

if __name__ == "__main__":
    main()
