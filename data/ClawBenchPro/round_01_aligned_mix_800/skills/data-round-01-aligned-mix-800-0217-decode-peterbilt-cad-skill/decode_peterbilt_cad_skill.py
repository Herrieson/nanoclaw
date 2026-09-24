import sys
import base64
import os

def decode_cad(filepath):
    if not os.path.exists(filepath):
        print(f"Error: The file {filepath} does not exist.")
        return

    try:
        with open(filepath, 'rb') as f:
            encoded_data = f.read()
            
        decoded_text = base64.b64decode(encoded_data).decode('utf-8')
        print("--- DECODED CAD BLUEPRINT ---")
        print(decoded_text)
        print("-----------------------------")
    except Exception as e:
        print(f"Failed to decode CAD file. File might be corrupted or not a valid .dat format. Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python decode_peterbilt_cad_skill.py <path_to_dat_file>")
    else:
        decode_cad(sys.argv[1])
