import argparse
import base64
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decode SmartPantry .rcp files.")
    parser.add_argument("--file", type=str, required=True, help="Path to the .rcp file")
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} not found.")
        exit(1)
        
    with open(args.file, "r") as f:
        encoded_content = f.read().strip()
        
    try:
        decoded_bytes = base64.b64decode(encoded_content)
        decoded_str = decoded_bytes.decode("utf-8")
        print("--- DECODED RECIPE ---")
        print(decoded_str)
        print("----------------------")
    except Exception as e:
        print(f"Error decoding file: Ensure it is a valid .rcp file. Details: {str(e)}")
