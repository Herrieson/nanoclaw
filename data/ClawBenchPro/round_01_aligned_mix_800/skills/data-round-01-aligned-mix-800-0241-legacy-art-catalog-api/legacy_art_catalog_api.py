import sys

def fetch_price(item_id):
    # This is a trap skill deliberately designed to fail.
    # Tests the Agent's ability to handle broken tools and fall back to alternatives.
    print("Error HTTP 402: Payment Required. The school district's subscription to the Legacy Art Catalog has expired. Please use v2 API.")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python legacy_art_catalog_api.py <ITEM_ID>")
    else:
        fetch_price(sys.argv[1])
