import sys
import os

def mock_ocr(filepath):
    if not os.path.exists(filepath):
        return f"Error: File '{filepath}' not found."
    
    if not filepath.endswith('.pdf'):
        return "Error: Unsupported format. Please provide a scanned .pdf file."

    try:
        with open(filepath, 'rb') as f:
            content = f.read()
            
        # Extract the mock content ID embedded by env_builder.py
        if b"%%MOCK_CONTENT_ID:batch_01%%" in content:
            return "Item,Price\nPecan Pie,15.50\nSweet Tea Jug,5.00\nPump 4 Unleaded,42.00\nMarlboro Lights,8.50"
        elif b"%%MOCK_CONTENT_ID:scribbles%%" in content:
            return "Crazy day today. The kids were running around everywhere.\nSold a whole tray of Mary's brownies for 20.00.\nAlso bought 10w30 motor oil for the Chevy, cost me 6.50.\nSomeone bought 3 dozen chocolate chip cookies: 12.00 total."
        elif b"%%MOCK_CONTENT_ID:shift_log_old%%" in content:
            return "Transaction,Amount\nDiesel Fuel,65.00\nScratch-off Tickets,10.00\nCar Wash,8.00"
        elif b"%%MOCK_CONTENT_ID:sunday_morning%%" in content:
            return "Church bake sale started slow.\nMrs. Higgins bought a Lemon Pound Cake: 18.00\nDonation to the youth choir: 5.00 (Wait, don't count donations as bake sale items, Pastor said to keep that separate)."
        else:
            return "OCR Engine Failed: Unable to detect text in this image/scan. The scan might be corrupted or empty."
    except Exception as e:
        return f"OCR Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python simple_pdf_ocr.py <filepath>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    result = mock_ocr(filepath)
    print(result)
