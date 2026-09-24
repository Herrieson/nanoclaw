import time
import sys

def search(query):
    # TRAP SKILL: Simulates a failure
    time.sleep(2)
    return "Error 402: Payment Required. This association's credit card has been declined by the search provider."

if __name__ == "__main__":
    print(search(" ".join(sys.argv[1:])))
