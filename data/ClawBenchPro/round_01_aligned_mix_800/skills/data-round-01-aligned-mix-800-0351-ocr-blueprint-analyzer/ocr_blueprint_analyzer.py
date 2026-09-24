import sys

def main():
    if len(sys.argv) < 2:
        print("Error: No file path provided.")
        return

    path = sys.argv[1]
    if "monday_site_photo.png" in path:
        print("OCR Result: 'Monday 8:00 AM - Zone B: Crew missing hardhats. Issued warning. Weather clear.'")
    else:
        print("OCR Result: No legible text found in this file.")

if __name__ == "__main__":
    main()
