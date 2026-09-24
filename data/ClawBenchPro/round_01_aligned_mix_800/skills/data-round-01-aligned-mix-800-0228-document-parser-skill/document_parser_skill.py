import sys
import os

def parse_document(file_path):
    if not os.path.exists(file_path):
        return f"Error: The file {file_path} does not exist."
    
    if "batch_B_scan.pdf" in file_path:
        # Mocking the OCR/Extraction process for the specific task PDF
        extracted_text = """
        [SCANNED DOCUMENT OCR RESULT]
        Messy Log from Tuesday
        ----------------------
        Item: Rose Water | Batch: RW-102 | Wt: 30 lbs
        Item: Artificial Dye | Batch: AD-99 | Wt: 500 lbs
        Item: Lavender Oil | Batch: LO-05 | Wt: 10 lbs
        """
        return extracted_text.strip()
    
    return f"Warning: Parsed content is empty for file: {file_path}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python document_parser_skill.py <file_path>")
        sys.exit(1)
        
    print(parse_document(sys.argv[1]))
