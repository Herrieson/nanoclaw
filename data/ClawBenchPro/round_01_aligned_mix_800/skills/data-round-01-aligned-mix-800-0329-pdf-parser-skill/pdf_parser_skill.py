import sys

def parse_pdf(path):
    # Simulated PDF parsing logic
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
            # Look for keywords in the mock PDF
            data = [line.strip() for line in lines if "Contractor" in line or "Cost" in line]
            return "\n".join(data) if data else "No readable text found in PDF."
    except Exception as e:
        return f"PDF Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(parse_pdf(sys.argv[1]))
