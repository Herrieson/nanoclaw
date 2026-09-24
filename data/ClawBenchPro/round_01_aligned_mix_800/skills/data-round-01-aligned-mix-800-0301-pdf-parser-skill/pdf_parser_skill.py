import sys

def parse_pdf(file_path):
    # Mock logic: Detect if it's the specific task file
    if "mariachi_invoice.pdf" in file_path:
        return """
        --- INVOICE: MARIACHI LOS TIGRES ---
        Date: Oct 12, 2023
        Service: Performance for Community Gathering
        Total Amount Due: $800.00
        Status: UNPAID (To be paid from collected funds)
        ------------------------------------
        """
    else:
        return "Error: Unsupported PDF format or file not found."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing file path")
    else:
        print(parse_pdf(sys.argv[1]))
