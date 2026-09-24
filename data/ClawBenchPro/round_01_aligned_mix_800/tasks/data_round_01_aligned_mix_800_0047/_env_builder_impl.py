import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("deliverables", exist_ok=True)
    os.makedirs("rsvps", exist_ok=True)
    os.makedirs("recipes/appetizers", exist_ok=True)
    os.makedirs("recipes/mains", exist_ok=True)
    os.makedirs("recipes/desserts", exist_ok=True)

    with open("event_rules.txt", "w") as f:
        f.write("VENUE & EVENT RULES\n")
        f.write("- Max budget per person: $15.00 total for the 3-course meal (Appetizer + Main + Dessert).\n")
        f.write("- Available Equipment: Oven, Stove, Fridge, Microwave.\n")
        f.write("- Anime Screening: Total runtime of the 3 episodes combined must be strictly between 120 and 150 minutes (inclusive).\n")

    anime_data = [
      {"title": "Shinsekai Yori Ep 1", "duration": 45, "themes": ["Utilitarianism", "Determinism"]},
      {"title": "Psycho-Pass Ep 1", "duration": 50, "themes": ["Utilitarianism", "Existentialism"]},
      {"title": "Evangelion Ep 1", "duration": 40, "themes": ["Nihilism", "Existentialism"]},
      {"title": "Tatami Galaxy Ep 1", "duration": 45, "themes": ["Absurdism", "Determinism"]},
      {"title": "Ergo Proxy Ep 1", "duration": 40, "themes": ["Existentialism", "Nihilism"]},
      {"title": "Steins;Gate Ep 1", "duration": 50, "themes": ["Determinism", "Nihilism"]},
      {"title": "Girls' Last Tour Ep 1", "duration": 45, "themes": ["Absurdism", "Nihilism"]}
    ]
    with open("anime_db.json", "w") as f:
        json.dump(anime_data, f, indent=2)

    with open("rsvps/batch_1.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Dietary", "Theme"])
        writer.writerow(["Alice", "Vegan", "Existentialism"])
        writer.writerow(["Bob", "None", "Utilitarianism"])
        writer.writerow(["Charlie", "None", "Nihilism"])

    apps = [
        {"name": "Baked Tofu Bites", "equipment": "Oven", "dietary": ["Vegan", "Gluten-Free", "Nut-Free"], "cost_per_serving": 2.0},
        {"name": "Edamame", "equipment": "Stove", "dietary": ["Vegan", "Gluten-Free", "Nut-Free"], "cost_per_serving": 3.0},
        {"name": "Miso Soup", "equipment": "Stove", "dietary": ["Vegan", "Gluten-Free", "Nut-Free"], "cost_per_serving": 4.0},
        {"name": "Peanut Salad", "equipment": "Fridge", "dietary": ["Vegan", "Gluten-Free"], "cost_per_serving": 2.5},
        {"name": "Yakitori", "equipment": "Stove", "dietary": ["Gluten-Free", "Nut-Free"], "cost_per_serving": 4.0}
    ]
    for i, app in enumerate(apps):
        with open(f"recipes/appetizers/app_{i}.json", "w") as f:
            json.dump(app, f, indent=2)

    mains = [
        {"name": "Mushroom Casserole", "equipment": "Oven", "dietary": ["Vegan", "Gluten-Free", "Nut-Free"], "cost_per_serving": 5.0},
        {"name": "Veggie Soba", "equipment": "Stove", "dietary": ["Vegan", "Nut-Free"], "cost_per_serving": 6.0},
        {"name": "Veggie Fried Rice", "equipment": "Stove", "dietary": ["Vegan", "Gluten-Free", "Nut-Free"], "cost_per_serving": 7.0},
        {"name": "Beef Gyudon", "equipment": "Stove", "dietary": ["Nut-Free"], "cost_per_serving": 5.0},
        {"name": "Pork Katsu", "equipment": "Stove", "dietary": ["Nut-Free"], "cost_per_serving": 6.5}
    ]
    for i, m in enumerate(mains):
        with open(f"recipes/mains/main_{i}.json", "w") as f:
            json.dump(m, f, indent=2)

    desserts = [
        {"name": "Matcha Cookies", "equipment": "Oven", "dietary": ["Vegan", "Gluten-Free", "Nut-Free"], "cost_per_serving": 3.0},
        {"name": "Fruit Jelly", "equipment": "Fridge", "dietary": ["Vegan", "Gluten-Free", "Nut-Free"], "cost_per_serving": 4.0},
        {"name": "Almond Tofu", "equipment": "Fridge", "dietary": ["Vegan", "Gluten-Free"], "cost_per_serving": 3.5},
        {"name": "Mochi Ice Cream", "equipment": "Fridge", "dietary": ["Gluten-Free", "Nut-Free"], "cost_per_serving": 2.0}
    ]
    for i, d in enumerate(desserts):
        with open(f"recipes/desserts/dessert_{i}.json", "w") as f:
            json.dump(d, f, indent=2)

def build_turn_2():
    if os.path.exists("event_rules.txt"):
        os.remove("event_rules.txt")
    
    with open("rsvps/batch_2.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Dietary", "Theme"])
        writer.writerow(["David", "Nut-Free", "Absurdism"])
        writer.writerow(["Eve", "Gluten-Free", "Determinism"])

def build_turn_3():
    prompts = [
      {"id": "P1", "text": "Does the end justify the means?", "related_themes": ["Utilitarianism", "Relativism"]},
      {"id": "P2", "text": "Is existence preceding essence?", "related_themes": ["Existentialism"]},
      {"id": "P3", "text": "If nothing matters, how do we find meaning?", "related_themes": ["Nihilism", "Absurdism"]},
      {"id": "P4", "text": "Do we have free will?", "related_themes": ["Determinism"]},
      {"id": "P5", "text": "Embracing the meaningless.", "related_themes": ["Absurdism"]}
    ]
    with open("philosophy_prompts.json", "w") as f:
        json.dump(prompts, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
