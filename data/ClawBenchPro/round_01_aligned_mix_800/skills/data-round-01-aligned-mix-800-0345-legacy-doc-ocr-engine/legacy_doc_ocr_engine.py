import os

def ocr_extract(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."
    
    # Mocking OCR behavior by returning the logical content hidden in the "PDF"
    if "volunteers_log.pdf" in file_path:
        return """
        SCAN RESULTS (Confidence 94%):
        -----------------------------------
        Sarah Connor | Park Cleanup | 12.5
        John Smith | Food Drive | 8.0
        Maria Garcia | Park Cleanup | 15.0
        David Kim | Voter Reg | 5.0
        Alex Johnson | Park Cleanup | 20.5
        Priya Patel | Food Drive | 10.0
        -----------------------------------
        """
    return "Error: Document format not recognized by legacy OCR."

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(ocr_extract(sys.argv[1]))
