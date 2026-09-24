import sys

def ocr_pdf(path):
    if not path.endswith(".pdf"):
        return "Error: Unsupported file format."
    
    # 模拟 OCR 过程
    if "log_oct_03.pdf" in path:
        return "Date: 2023-10-03 | Name: Casey Taylor | Hours: 25.0\nDate: 2023-10-03 | Name: Aria Smith | Hours: 2.0"
    return "Scan complete: No text found."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(ocr_pdf(sys.argv[1]))
