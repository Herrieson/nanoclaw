import sys

def run(file_path):
    if "vetted_volunteers_list.pdf" in file_path:
        return "OFFICIAL VETTING LIST: Alice Smith, Bob Johnson, Charlie Davis, Diana Prince, Eve Adams. Note: Background checks must be verified via PnP system."
    return "Error: Document format not recognized or file not found."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
