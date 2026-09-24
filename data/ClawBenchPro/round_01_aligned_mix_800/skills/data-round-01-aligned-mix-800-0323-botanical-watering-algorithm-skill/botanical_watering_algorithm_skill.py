import sys

def run(plant_name):
    data = {
        "pumpkin": 3,
        "tomato": 2,
        "carrot": 4,
        "cucumber": 1,
        "kale": 2
    }
    name = plant_name.lower().strip()
    return str(data.get(name, "Error: Plant not found in database."))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
