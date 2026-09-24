import sys
import base64
import zlib
import argparse

def parse_rpd(file_path):
    try:
        with open(file_path, "rb") as f:
            encoded_data = f.read()
        
        compressed_data = base64.b64decode(encoded_data)
        csv_string = zlib.decompress(compressed_data).decode('utf-8')
        
        return f"Successfully parsed {file_path}:\n\n{csv_string}"
    except Exception as e:
        return f"Error parsing RPD file: {str(e)}. Make sure the file path is correct and it is a valid .rpd file."

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse .rpd file")
    parser.add_argument("file_path", help="Path to the .rpd file")
    args = parser.parse_args()
    print(parse_rpd(args.file_path))
