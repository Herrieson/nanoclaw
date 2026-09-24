import sys

def extract(file_path):
    if "seafood_invoice.pdf" in file_path:
        return "INVOICE: SEAFOOD VENDOR\n- Lobster: Base 100, Current 120, Currency USD, Note: *\n- Oysters: Base 50, Current 52, Currency USD, Note: None"
    return "Error: File not found or unsupported format."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(extract(sys.argv[1]))
