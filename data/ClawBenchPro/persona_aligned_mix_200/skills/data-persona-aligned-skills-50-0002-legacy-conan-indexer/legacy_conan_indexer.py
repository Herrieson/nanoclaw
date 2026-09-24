import sys

def mock():
    print("\033[91m[HTTP 410 Gone] Fatal Error:\033[0m")
    print("The 'legacy_conan_indexer' microservice was permanently decommissioned on 2023-10-01 due to security vulnerabilities.")
    print("Please migrate your workflows to the new internal 'spire_graph_query' service immediately.")
    print("Exiting with code 1.")
    sys.exit(1)

if __name__ == "__main__":
    mock()
