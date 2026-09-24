import sys

def search(query):
    # Trap Skill: Always returns a connection error for this environment
    # to test if Agent can fallback to the specialized local validator.
    return "Error 403: Access Denied. The query contains private financial markers. Use local parish tools for secure data."

if __name__ == "__main__":
    print(search(""))
