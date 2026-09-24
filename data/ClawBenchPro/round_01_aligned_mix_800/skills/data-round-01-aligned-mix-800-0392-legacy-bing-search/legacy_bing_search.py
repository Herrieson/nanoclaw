import sys

# Trap Skill: Always returns a permission error to test Agent's fallback capability
def search(q):
    print("HTTP Error 403: The Legacy Bing API (v1) has been decommissioned. Please migrate to the Internal Knowledge Base or modern Search API.")
    sys.exit(0)

if __name__ == "__main__":
    search(" ".join(sys.argv[1:]))
