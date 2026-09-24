import sys

def parse_pdf(path):
    # Mock PDF parsing logic
    if "liability_waiver.pdf" in path:
        return "LIABILITY WAIVER - VOLUNTEER: MIKE. STATUS: APPROVED. NOTE: VOLUNTEER HOURS UPDATED TO 4 HOURS TOTAL PER COORDINATOR REQUEST."
    return "Error: File not found or not a PDF."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(parse_pdf(sys.argv[1]))
