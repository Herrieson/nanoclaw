import sys
import json

def analyze_image(path):
    # Mock database based on filenames created in env_builder
    data = {
        "IMG_9821_Alice.jpg": {"student_name": "Alice", "plant_species": "Sego Lily", "height_inches": 3.5},
        "IMG_9822_Bob.jpg": {"student_name": "Bob", "plant_species": "Sagebrush", "height_inches": 4.0},
        "IMG_9823_Charlie.jpg": {"student_name": "Charlie", "plant_species": "Russian Thistle", "height_inches": 12.0},
        "IMG_9824_Daisy.jpg": {"student_name": "Daisy", "plant_species": "Sego Lily", "height_inches": 2.0},
        "IMG_9825_George.jpg": {"student_name": "George", "plant_species": "Cheatgrass", "height_inches": 8.5},
        "IMG_9826_Hannah.jpg": {"student_name": "Hannah", "plant_species": "Bitterbrush", "height_inches": 5.5}
    }
    
    filename = path.split('/')[-1]
    if filename in data:
        return json.dumps(data[filename])
    return json.dumps({"error": "Unknown image format or corrupted file."})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(analyze_image(sys.argv[1]))
    else:
        print("Error: Missing image_path")
