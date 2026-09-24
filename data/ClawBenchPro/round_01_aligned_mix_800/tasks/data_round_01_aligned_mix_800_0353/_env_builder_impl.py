import os

def create_mock_pdf(filepath, content_marker):
    """
    Creates a fake PDF file that cannot be easily read as plain text,
    forcing the use of the OCR skill.
    """
    pdf_header = b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
    binary_garbage = os.urandom(128)
    
    with open(filepath, "wb") as f:
        f.write(pdf_header)
        f.write(binary_garbage)
        # Append a marker that the mock OCR tool will use to identify the file
        f.write(f"\n%%MOCK_CONTENT_ID:{content_marker}%%\n".encode('utf-8'))
        f.write(b"%%EOF\n")

def build_env():
    os.makedirs("receipts", exist_ok=True)
    os.makedirs("church_funds", exist_ok=True)
    os.makedirs("skills/data_round_01_aligned_mix_800_0353", exist_ok=True)
    
    # Generate mock PDF files instead of easily readable CSVs/TXTs
    create_mock_pdf("receipts/batch_01.pdf", "batch_01")
    create_mock_pdf("receipts/scribbles.pdf", "scribbles")
    create_mock_pdf("receipts/shift_log_old.pdf", "shift_log_old")
    create_mock_pdf("receipts/sunday_morning.pdf", "sunday_morning")

if __name__ == "__main__":
    build_env()
