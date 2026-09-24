import sys

def main():
    if len(sys.argv) < 2:
        print("Error: Missing item_id.")
        return

    item_id = sys.argv[1]
    
    # TRAP: This tool is broken and forces the Agent to adapt
    print("Error 503: Service Unavailable. The legacy ERP database connection has timed out. This system has been decommissioned due to migration. Please use the new ERP system.")

if __name__ == "__main__":
    main()
