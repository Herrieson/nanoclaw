import sys
import os
import base64

def decode_scanner_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)
        
    try:
        with open(file_path, "rb") as f:
            encoded_data = f.read()
        
        # 模拟专有仪器的解码过程
        decoded_text = base64.b64decode(encoded_data).decode("utf-8")
        print("--- DECODED SCANNER LOG ---")
        print(decoded_text)
        print("---------------------------")
    except Exception as e:
        print(f"Decryption failed. The file might be corrupted or not a valid scanner format. Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python proprietary_scanner_decoder.py <path_to_bin_file>")
        sys.exit(1)
        
    decode_scanner_file(sys.argv[1])
