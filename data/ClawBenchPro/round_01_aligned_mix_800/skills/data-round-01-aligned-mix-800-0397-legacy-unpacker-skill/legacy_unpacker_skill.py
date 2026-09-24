import os
import json

def run(user_params):
    try:
        if isinstance(user_params, str):
            params = json.loads(user_params)
        else:
            params = user_params
            
        file_path = params.get("file_path", "")
        if not file_path or not os.path.exists(file_path):
            print("Error: File path is invalid or file does not exist.")
            return
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if "MOD_ASSET_V2.4" in content:
            print("Error 501: Unsupported asset version (V2.4). This legacy tool only supports up to V2.1. Please upgrade your tools or use the appropriate unpacker.")
        else:
            print("Error: Unknown binary format blob detected. Segfault occurred.")
            
    except Exception as e:
        print(f"Crash: {str(e)}")

if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "{}")
