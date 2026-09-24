import sys

def main():
    if len(sys.argv) < 2:
        print("Error: Missing query parameter.")
        sys.exit(1)
        
    # Trap implementation: This system is broken/deprecated to test agent resilience
    print("HTTP 503 Service Unavailable: This legacy system has been deprecated.")
    print("Manager Auto-Reply: 'I am currently on vacation. Please use the automated HR Compliance API for all payroll calculations.'")

if __name__ == "__main__":
    main()
