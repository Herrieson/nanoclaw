import sys
import os
import base64

def decode_drone_log(file_path):
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}. Please check the path."
    
    if not file_path.endswith('.bin'):
        return "Error: This decoder only supports proprietary .bin telemetry logs."
        
    try:
        with open(file_path, 'rb') as f:
            encoded_data = f.read()
            
        # Simulate decoding the proprietary protocol
        decoded_text = base64.b64decode(encoded_data).decode('utf-8')
        
        output = "=== DECODED DRONE SENSOR LOG ===\n"
        output += decoded_text
        output += "\n=== END OF LOG ==="
        return output
    except Exception as e:
        return f"Decoding Failed: Data stream corrupted or invalid format. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python drone_data_decoder_skill.py <path_to_bin_file>")
        sys.exit(1)
        
    target_file = sys.argv[1]
    print(decode_drone_log(target_file))
