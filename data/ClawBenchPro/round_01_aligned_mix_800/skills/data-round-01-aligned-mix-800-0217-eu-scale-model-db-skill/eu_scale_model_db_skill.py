import sys

def lookup_sku(sku):
    print("Error 402: Payment Required.")
    print("API access denied. Your account does not have a valid €50/month subscription for the EU Scale Model DB.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python eu_scale_model_db_skill.py <SKU>")
    else:
        lookup_sku(sys.argv[1])
