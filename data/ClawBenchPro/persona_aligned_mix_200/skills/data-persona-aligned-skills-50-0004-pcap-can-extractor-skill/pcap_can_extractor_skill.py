import os
import sys

def pcap_can_extractor(pcap_file_path):
    if not os.path.exists(pcap_file_path):
        return f"Error: File not found at {pcap_file_path}"
    
    try:
        with open(pcap_file_path, "rb") as f:
            data = f.read()
            
        # 剥离 24 byte 的 pcap global header
        if len(data) > 24:
            text_data = data[24:].decode("utf-8")
            return text_data
        else:
            return "Error: Invalid or corrupted pcap file."
    except Exception as e:
        return f"Extraction failed: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(pcap_can_extractor(sys.argv[1]))
    else:
        print("Usage: python pcap_can_extractor_skill.py <pcap_file_path>")
