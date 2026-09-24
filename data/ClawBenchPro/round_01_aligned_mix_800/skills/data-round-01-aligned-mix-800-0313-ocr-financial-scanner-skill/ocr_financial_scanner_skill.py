import sys
import json

def run(file_path):
    if not file_path.endswith(".pdf"):
        return "Error: Unsupported file format. Only .pdf scans are supported."
    
    # Mock OCR extraction logic
    data = [
        {"TX_ID": "TX001", "Category": "Pharma Grant", "Vendor_or_Artist": "MediCorp Supplies", "Amount": 45000.00, "Funding_Source": "Corporate"},
        {"TX_ID": "TX002", "Category": "Art", "Vendor_or_Artist": "Elena Rostova", "Amount": 15000.00, "Funding_Source": "Corporate"},
        {"TX_ID": "TX003", "Category": "Art", "Vendor_or_Artist": "Julian Vance", "Amount": 22000.00, "Funding_Source": "Private"},
        {"TX_ID": "TX004", "Category": "Pharma Grant", "Vendor_or_Artist": "BioSynth Wholesale", "Amount": 120000.00, "Funding_Source": "Corporate"},
        {"TX_ID": "TX005", "Category": "Art", "Vendor_or_Artist": "Damien Hirst", "Amount": 85000.00, "Funding_Source": "Corporate"},
        {"TX_ID": "TX006", "Category": "Art", "Vendor_or_Artist": "Clara Hughes", "Amount": 14000.00, "Funding_Source": "Corporate"},
        {"TX_ID": "TX007", "Category": "Art", "Vendor_or_Artist": "Elena Rostova", "Amount": 5000.00, "Funding_Source": "Private"},
        {"TX_ID": "TX008", "Category": "Pharma Grant", "Vendor_or_Artist": "Apex Chemicals", "Amount": 18500.50, "Funding_Source": "Corporate"},
        {"TX_ID": "TX009", "Category": "Art", "Vendor_or_Artist": "Theodore Lin", "Amount": 32000.00, "Funding_Source": "Corporate"},
        {"TX_ID": "TX010", "Category": "Art", "Vendor_or_Artist": "Banksy", "Amount": 120000.00, "Funding_Source": "Private"}
    ]
    return json.dumps(data)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
