import sys

def main():
    if len(sys.argv) < 2:
        print("Error: No file path.")
        return
    
    path = sys.argv[1]
    if "vendor_lookup.pdf" in path:
        print("VENDOR CLASSIFICATION DOCUMENT\nV-99: Industrial Safety Supplies Corp (Category S)\nV-22: Creative Minds Art Emporium (Category A)")
    else:
        print("Error: Could not read PDF or file is empty.")

if __name__ == "__main__":
    main()
