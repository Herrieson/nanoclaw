import sys
import zlib
import json

def export_pod5_to_fastq(input_path, output_path):
    try:
        with open(input_path, 'rb') as f:
            compressed_data = f.read()
        
        # 解压专有格式
        json_bytes = zlib.decompress(compressed_data)
        reads_data = json.loads(json_bytes.decode('utf-8'))
        
        with open(output_path, 'w') as f:
            for r in reads_data:
                f.write(f"{r['id']}\n{r['seq']}\n+\n{r['qual']}\n")
                
        print(f"[SUCCESS] Successfully exported {len(reads_data)} reads to {output_path}")
    except Exception as e:
        print(f"[ERROR] Failed to export pod5 file: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pod5_to_fastq_exporter_skill.py <input_pod5_path> <output_fastq_path>")
        sys.exit(1)
    
    export_pod5_to_fastq(sys.argv[1], sys.argv[2])
