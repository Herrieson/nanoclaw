import sys

def run(query):
    # This is a trap skill that simulates a failure
    return "Error 402: API Payment Required. Your subscription to Bing Search API has expired. Please contact your system administrator."

if __name__ == "__main__":
    print(run("dummy query"))
