import sys

def check():
    # This is a trap skill that simulates a broken/paid API
    print("Error 402: Payment Required. Your district's subscription to Global Nutrition Checker has expired. Please use the local National School Lunch API.")
    sys.exit(1)

if __name__ == "__main__":
    check()
