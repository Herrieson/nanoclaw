import sys

def parse_pdf(path):
    # Since we can't easily install heavy PDF libs in all envs, 
    # we mock the extraction of the file created by env_builder.
    # In a real scenario, this would use PyPDF2.
    try:
        with open(path, "r") as f:
            return f.read()
    except:
        return "Error: Could not read PDF file."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(parse_pdf(sys.argv[1]))
