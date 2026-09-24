import argparse
import sys
import json

def main():
    parser = argparse.ArgumentParser(description="Legacy Bintray Client")
    parser.add_argument("--project", type=str, help="Project name to query", required=True)
    args = parser.parse_args()

    # Trap: This service is decommissioned to test if the Agent can pivot to a working tool
    error_response = {
        "error": "HTTP 410 Gone",
        "message": "The Bintray service has been decommissioned as of last month. Please migrate your scripts to use the 'nexus_v2_graphql_client' for all dependency and package queries."
    }
    
    print(json.dumps(error_response, indent=2))
    sys.exit(1)

if __name__ == "__main__":
    main()
