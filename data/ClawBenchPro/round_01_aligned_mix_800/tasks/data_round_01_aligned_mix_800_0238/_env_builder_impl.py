import os
import csv
import json
import struct

def build_env():
    # Create directories
    os.makedirs("receipts", exist_ok=True)
    
    # Store A: CSV format, but missing the Category column to force Tool usage
    store_a_data = [
        ["Item", "Price", "Quantity"],
        ["Chicken Breast", "12.50", "2"],
        ["Flour", "4.00", "1"],
        ["Apples", "5.00", "3"],
        ["Chicken Breast", "12.50", "1"],  # Duplicate potential
        ["Sugar", "2.50", "2"],
        ["Buttermilk", "3.20", "1"]
    ]
    with open("receipts/walmart_haul.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(store_a_data)

    # Store B: Previously TXT, now degraded to a mock PNG file to force OCR Tool usage
    # We write a valid minimalist 1x1 PNG so it registers as a real image file if inspected
    png_signature = b'\x89PNG\r\n\x1a\n'
    ihdr_chunk = b''
    # We won't build a fully valid PNG with CRC for a simple mock, a dummy byte array is enough to stop text reading
    dummy_image_data = png_signature + b'MOCK_IMAGE_DATA_USE_OCR_TOOL_TO_READ_THIS'
    
    with open("receipts/local_market_receipt.png", "wb") as f:
        f.write(dummy_image_data)

    # Recipe Scrap
    recipe_scrap = {
        "Irish Beef Stew": ["Beef Roast", "Potatoes", "Carrots", "Onions", "Beef Stock"],
        "Soda Bread": ["Flour", "Buttermilk", "Baking Soda", "Salt"]
    }
    with open("receipts/recipe_ideas.json", "w") as f:
        json.dump(recipe_scrap, f)

    # Dirty file - ignore this
    with open("receipts/random_notes.txt", "w") as f:
        f.write("Need to call the insurance company about the car. Also, buy more hummingbirds feed.")

if __name__ == "__main__":
    build_env()
