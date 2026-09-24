import struct
import json
import sys

def parse_bin(file_path):
    results = []
    try:
        with open(file_path, "rb") as f:
            while True:
                chunk_id = f.read(4)
                if not chunk_id: break
                chunk_dur = f.read(4)
                if not chunk_dur: break
                
                uid = chunk_id.decode('ascii')
                duration = struct.unpack("i", chunk_dur)[0]
                results.append({"id": uid, "duration": duration})
        return json.dumps(results)
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(parse_bin(sys.argv[1]))
