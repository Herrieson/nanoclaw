import struct
import json
import os

def extract_binary_data(file_path):
    if not os.path.exists(file_path):
        return json.dumps({"error": "File not found"})
    
    results = []
    # Format: 4s (BatchID), 8s (Reactor), f (Temp), f (Weight), f (Recycled), f (Output)
    record_size = struct.calcsize("4s8sffff")
    
    try:
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(record_size)
                if len(chunk) < record_size:
                    break
                bid, rid, temp, weight, recycled, output = struct.unpack("4s8sffff", chunk)
                results.append({
                    "batch_id": bid.decode('ascii').strip(),
                    "reactor_id": rid.decode('ascii').strip(),
                    "temp_c": round(temp, 2),
                    "total_weight_kg": round(weight, 2),
                    "recycled_content_kg": round(recycled, 2),
                    "output_product_kg": round(output, 2)
                })
        return json.dumps(results)
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(extract_binary_data(sys.argv[1]))
