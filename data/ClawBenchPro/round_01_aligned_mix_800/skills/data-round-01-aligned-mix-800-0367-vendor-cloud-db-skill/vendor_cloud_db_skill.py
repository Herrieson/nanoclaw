import sys

def main():
    if len(sys.argv) < 2:
        print("Error: Missing batch_id parameter.")
        return
    
    # Intentionally broken as per the persona constraint (trap skill)
    print("HTTP 402 Payment Required: Subscription expired for this institutional account. Please contact vendor support.")

if __name__ == "__main__":
    main()
