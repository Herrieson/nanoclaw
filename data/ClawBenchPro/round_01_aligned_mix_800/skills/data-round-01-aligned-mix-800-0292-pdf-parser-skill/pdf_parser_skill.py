import sys
import os

def parse_pdf(path):
    filename = os.path.basename(path)
    if "restricted_antiques" in filename:
        return "RESTRICTED ANTIQUE COLLECTION - INTERNAL USE ONLY\nID: B-101\nID: B-102\nID: B-103"
    elif "manual_logs" in filename:
        return """
        HANDWRITTEN LOGS OCT 2023:
        - Timmy Smith took B-001, due 2023-11-01.
        - Mary Johnson borrowed B-101. Due date: 2023-09-12.
        - Bobby Tables borrowed B-102. Return by 2023-10-15.
        - Alice Vance took B-103. Due: 2023-08-30.
        """
    return "Error: File format not recognized or encrypted."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_parser_skill.py <path>")
    else:
        print(parse_pdf(sys.argv[1]))
