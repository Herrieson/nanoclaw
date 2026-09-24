import sys
import json

def parse_pdf(path):
    if "batch_02.pdf" in path:
        return [
            {"sku": "SKU-005", "item_name": "Sustainable Oats", "vendor_id": "V-2201", "expiry_date": "2024-08-20", "unit_price": 3.5, "quantity": 20},
            {"sku": "SKU-006", "item_name": "Organic Berries", "vendor_id": "V-1102", "expiry_date": "2023-12-28", "unit_price": 4.0, "quantity": 15}
        ]
    return "Error: Unsupported file format or unreadable scan."

if __name__ == "__main__":
    print(json.dumps(parse_pdf(sys.argv[1])))
