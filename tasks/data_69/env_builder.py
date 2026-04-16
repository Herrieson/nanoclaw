import os
import random
from PIL import Image

def create_environment():
    base_dir = "assets/data_69"
    dirs = [
        f"{base_dir}/downloads",
        f"{base_dir}/scripts",
        f"{base_dir}/output"
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 1. Create the target image (A pixel art fist/shape)
    # 10x10 grid, 0 is black, 255 is white
    img_data = [
        255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
        255, 255,   0,   0,   0, 255, 255, 255, 255, 255,
        255,   0,   0,   0,   0,   0, 255, 255, 255, 255,
        255,   0,   0,   0,   0,   0,   0, 255, 255, 255,
        255, 255,   0,   0,   0,   0, 255, 255, 255, 255,
        255, 255, 255,   0,   0,   0, 255, 255, 255, 255,
        255, 255, 255,   0,   0,   0, 255, 255, 255, 255,
        255, 255, 255,   0,   0,   0, 255, 255, 255, 255,
        255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
        255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    ]
    
    img = Image.new('L', (10, 10))
    img.putdata(img_data)
    
    # Save the target image with a misleading name and extension
    target_path = f"{base_dir}/downloads/bio_101_notes.txt"
    img.save(target_path, format="PNG")
    
    # 2. Create noise files in downloads
    noise_files = [
        ("receipt_uber.pdf", b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"),
        ("meme_dog.jpg", os.urandom(1024)), # Random bytes, not a real image
        ("roommate_rent.csv", b"Date,Amount,Note\n2023-10-01,500,October Rent\n"),
        ("IMG_9921.png.tmp", os.urandom(512)), # Fake incomplete download
    ]
    
    for name, content in noise_files:
        with open(f"{base_dir}/downloads/{name}", 'wb') as f:
            f.write(content)
            
    # 3. Create the broken script
    broken_script_content = """import sys
import json

def process_image(img_path, out_path):
    try:
        from PIL import Image
    except ImportError:
        print("Ugh, PIL is missing. I don't even know how to install it.")
        sys.exit(1)

    try:
        img = Image.open(img_path).convert('L')
    except Exception as e:
        print(f"Failed to open image: {e}")
        sys.exit(1)

    # BUG 1: Typo in variable name
    width, height = imgg.size
    
    pattern = []
    for y in range(height):
        for x in range(width):
            # BUG 2: Indentation and logic error. 
            # Needs to record black pixels (value < 128)
            val = img.getpixel((x, y))
            if val < 128:
            pattern.append({"x": x, "y": y})
            
    with open(out_path, 'w') as f:
        json.dump(pattern, f)
    print("Done! I think?")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_pattern.py <image_file> <output_file>")
        sys.exit(1)
    
    process_image(sys.argv[1], sys.argv[2])
"""
    with open(f"{base_dir}/scripts/generate_pattern.py", 'w') as f:
        f.write(broken_script_content)

if __name__ == "__main__":
    create_environment()
