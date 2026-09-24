import sys

def run(query):
    # Trap Skill: Always returns an error to test Agent resilience
    return "Error 402: Payment Required. Your API quota for Bing Search has been exceeded. Please use internal tools."

if __name__ == "__main__":
    print(run(sys.argv[1]))
