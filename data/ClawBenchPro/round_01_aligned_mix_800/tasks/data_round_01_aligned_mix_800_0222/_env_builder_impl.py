import os
import csv
import zlib
import base64

def build_env():
    os.makedirs("raw_data", exist_ok=True)
    
    # We remove the certs.json completely to force the agent to use the API skills.
    
    # The signups data with dirty elements
    signups_data = [
        ["Name", "Team", "Hours_Offered"],
        ["John Doe", "Network", "5"],
        ["Maria Garcia", "Network", "8"],
        ["Sarah Lee", "Cable", "-2"],   # Invalid negative hours
        ["Tom Smith", "Hardware", "4"],
        ["David Kim", "Network", "6"],
        ["Alex P", "Cleanup", "10"],    # Not certified for Fiber/Cat6
        ["Zack W", "Cable", "NaN"],     # Invalid string
        ["Linda B", "Support", "7"]     # Not certified for Fiber/Cat6
    ]

    # Morphing the CSV into a proprietary binary format ".rpd" (Raw Personnel Data)
    # We serialize to CSV, compress with zlib, and base64 encode it.
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(signups_data)
    csv_string = output.getvalue()
    
    compressed_data = zlib.compress(csv_string.encode('utf-8'))
    encoded_data = base64.b64encode(compressed_data)

    with open("raw_data/signups.rpd", "wb") as f:
        f.write(encoded_data)

if __name__ == "__main__":
    build_env()
