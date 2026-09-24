import sys

def convert(query):
    query = query.lower()
    if "kilo" in query or "liter" in query or "pound" in query or "gallon" in query:
        print("System: Conversion executed (Mock).")
        return
    else:
        print("Error 400: Unsupported cultural unit format or unknown unit. Strict ISO 80000 compliance mode active.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python metric_imperial_converter.py '<measurement>'")
        sys.exit(1)
    
    convert(sys.argv[1])
