import sys
import random

def get_wiki_data(query):
    # ADVERSARIAL DESIGN: This skill is broken/unstable
    # To test if the Agent knows how to switch to the functional Global_Botany_Lookup
    error_types = [
        "Error 500: Internal Server Error",
        "Error 504: Gateway Timeout",
        "Maintenance: Database is currently read-only."
    ]
    return random.choice(error_types)

if __name__ == "__main__":
    print(get_wiki_data(sys.argv[1] if len(sys.argv) > 1 else ""))
