import sys

def parse_pdf(path):
    # In this mock environment, we read the 'fake' pdf content created by env_builder
    try:
        with open(path, 'r') as f:
            return f.read()
    except:
        return "Error: Could not read PDF file."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(parse_pdf(sys.argv[1]))
