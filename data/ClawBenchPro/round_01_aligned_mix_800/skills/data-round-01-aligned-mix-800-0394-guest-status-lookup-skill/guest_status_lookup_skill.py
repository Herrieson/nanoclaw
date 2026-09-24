import sys

def lookup(name):
    vips = ["mr. anderson", "isabella torres", "julian vance", "sophia sterling", "marcus reed"]
    name_clean = name.strip().lower()
    if name_clean in vips:
        return "VIP"
    elif name_clean in ["crash override", "lucia gomez"]:
        return "CRASHER"
    return "NOT_FOUND"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(lookup(" ".join(sys.argv[1:])))
