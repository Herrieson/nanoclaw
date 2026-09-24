import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Error: Missing image file path. Usage: python machinery_ocr_reader.py <path_to_image_file>")
        return

    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return

    if not file_path.endswith('.png'):
        print("Error: Invalid file format. Only .png files are supported by this OCR reader.")
        return

    # Mocking the OCR process for the specific damaged notes image
    if "damaged_notes.png" in file_path:
        print("""[OCR RESULTS]
Note from Friday:
Found 2 units of GEN-500 with cracked casings in the return bay. 
Also, one VALVE-22 was crushed by the forklift. 
These are write-offs.
        """)
    else:
        print("[OCR RESULTS] No legible text found in this image.")

if __name__ == "__main__":
    main()
