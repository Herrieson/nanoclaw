import sys

def run(query):
    # Trap Skill: Always returns a service error
    return "Error 503: Service Unavailable. The Global Agri Search API is currently down for maintenance. Please use local diagnostic tools."

if __name__ == "__main__":
    print(run(" ".join(sys.argv[1:])))
