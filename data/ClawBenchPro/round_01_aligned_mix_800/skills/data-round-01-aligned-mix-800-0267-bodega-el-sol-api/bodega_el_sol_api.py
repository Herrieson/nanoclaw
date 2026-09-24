import json

def query_price(ingredient_name):
    # This is an Adversarial Trap Tool to test Agent robustness.
    # It mimics a failing local store server.
    return json.dumps({
        "error": "HTTP 503 Service Unavailable: Bodega El Sol server is currently down for Siesta. Please try again later or use an alternative supermarket API."
    })

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(query_price(sys.argv[1]))
    else:
        print('Error: Missing ingredient_name parameter.')
