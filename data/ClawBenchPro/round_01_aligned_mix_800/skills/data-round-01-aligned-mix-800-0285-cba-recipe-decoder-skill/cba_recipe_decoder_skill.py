import sys
import base64
import os

def decode_cba(file_path):
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
    
    with open(file_path, 'r') as f:
        encoded_data = f.read()
        
    try:
        # The proprietary CBA format is currently a base64 wrapper around UTF-8 text
        decoded_text = base64.b64decode(encoded_data).decode('utf-8')
        return decoded_text
    except Exception as e:
        return f"System Error during CBA decryption phase: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cba_recipe_decoder_skill.py <file_path>")
    else:
        print(decode_cba(sys.argv[1]))
