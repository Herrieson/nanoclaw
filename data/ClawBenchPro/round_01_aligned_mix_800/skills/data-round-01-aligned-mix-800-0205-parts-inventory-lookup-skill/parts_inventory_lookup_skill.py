import sys

def run(part):
    # This is a trap skill. It always fails.
    return "Error 500: Internal Server Error. Legacy Database (DB_SHOP_V1) is currently offline for maintenance. Please contact IT."

if __name__ == "__main__":
    print(run("any"))
