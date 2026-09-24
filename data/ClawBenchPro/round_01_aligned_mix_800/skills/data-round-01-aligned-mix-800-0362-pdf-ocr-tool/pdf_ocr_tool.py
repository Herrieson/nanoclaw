import sys

def run(file_path):
    if "morning_scan.pdf" in file_path:
        # Mocking the OCR result of the scanned morning shift
        return "Student_Name,Grade,Hours\nLeo,5,4\nMia,6,5\nZoe,5,3\nCarlos,4,2"
    return "Error: File not found or not a valid PDF."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
