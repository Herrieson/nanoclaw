import sys

def run(file_path):
    if "scanned_responses_batch_2.jpg" not in file_path:
        return "Error: File not found or unsupported format."
    
    # Mocked OCR output for the specific task file
    data = [
        "name,status,package,base_fee",
        "Charlie Brown,Pending,Standard,500",
        "Daisy Miller,Paid,Premium,600",
        "Jack Sparrow,Paid,Premium,600",
        "Fiona Gallagher,Paid,Premium,700"
    ]
    return "\n".join(data)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
