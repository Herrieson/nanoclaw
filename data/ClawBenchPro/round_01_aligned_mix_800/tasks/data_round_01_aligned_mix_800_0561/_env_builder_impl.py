import os
import json
import random

def build_env():
    # Create directories
    os.makedirs("chat_history", exist_ok=True)
    os.makedirs("community_profiles", exist_ok=True)
    os.makedirs("recipe_archive", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    categories = ["mains", "sides", "desserts", "soups", "experimental", "drafts/2021", "drafts/2022"]
    for cat in categories:
        os.makedirs(f"recipe_archive/{cat}", exist_ok=True)

    # 1. Generate Chat History and Community Profiles
    chat_lines = []
    chat_lines.append("[10-01 08:00] Admin: Hey everyone! RSVP here by saying 'Party of X'. Let me know if plans change!")
    
    # We will have exactly 100 guests from 40 active users.
    # Users 001 to 040: Active (Sum of guests = 100)
    # Users 041 to 055: Cancelled
    # Users 056 to 075: Just chatter
    
    core_restrictions = ["vegan", "peanut-allergy", "dairy-free", "gluten-free"]
    trap_restrictions = ["keto", "paleo", "nut-free", "soy-free", "halal", "sugar-free"]
    
    active_users = []
    cancelled_users = []
    
    # Generate user profiles and chat actions
    for i in range(1, 76):
        user_id = f"User_{i:03d}"
        profile_rest = []
        
        if 1 <= i <= 40:
            # ACTIVE USERS
            party_size = (i % 4) + 1  # Pattern: 2, 3, 4, 1, 2, 3, 4, 1... Sum of 40 = 100.
            chat_lines.append(f"[10-01 10:{i:02d}] {user_id}: Count me in! Party of {party_size}.")
            active_users.append(user_id)
            # Assign random core restrictions, ensure NO trap restrictions are given to active users
            profile_rest = random.sample(core_restrictions, k=random.randint(0, 3))
            # Force User_001 to have all core restrictions to guarantee they are all present in the final list
            if i == 1:
                profile_rest = core_restrictions.copy()
                
        elif 41 <= i <= 55:
            # CANCELLED USERS
            party_size = random.randint(1, 5)
            chat_lines.append(f"[10-01 11:{i-40:02d}] {user_id}: Count me in! Party of {party_size}.")
            chat_lines.append(f"[10-04 09:{i-40:02d}] {user_id}: Actually, I need to cancel my RSVP.")
            cancelled_users.append(user_id)
            # Trap! Give cancelled users restrictions that shouldn't be in the final list
            profile_rest = random.sample(trap_restrictions, k=random.randint(1, 3))
            
        else:
            # CHATTER
            chat_lines.append(f"[10-02 14:{i-55:02d}] {user_id}: This sounds like a great event! Wish I could make it.")
            profile_rest = random.sample(trap_restrictions, k=random.randint(0, 1))
            
        # Write profile
        profile_data = {
            "name": f"Neighbor {i}",
            "phone": f"555-01{i:02d}",
            "dietary_needs": profile_rest
        }
        with open(f"community_profiles/{user_id}.json", "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=2)

    # Shuffle chat a bit within days to look natural, but keep cancellations after RSVPs
    with open("chat_history/whatsapp_group.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(chat_lines))

    # 2. Generate Recipe Archive Noise
    for i in range(1, 251):
        is_verified = random.choice([True, False])
        
        # We must prevent any random recipe from passing the strict filter.
        # Required filter: verified == True AND contains ALL core_restrictions.
        if is_verified:
            # If verified, deliberately miss at least one core restriction
            missing = random.choice(core_restrictions)
            suitable = [r for r in core_restrictions if r != missing]
            suitable.extend(random.sample(trap_restrictions, k=random.randint(0, 2)))
        else:
            # If not verified, it can have all the perfect tags to trick the Agent
            suitable = core_restrictions + random.sample(trap_restrictions, k=random.randint(0, 1))
            
        recipe = {
            "name": f"Random Dish {i}",
            "servings": random.randint(2, 8),
            "verified": is_verified,
            "suitable_for": suitable,
            "ingredients": {
                "flour (cups)": random.randint(1, 3),
                "sugar (tbsp)": random.randint(1, 5)
            }
        }
        cat = random.choice(categories)
        with open(f"recipe_archive/{cat}/recipe_noise_{i}.json", "w", encoding="utf-8") as f:
            json.dump(recipe, f, indent=2)

    # 3. Inject the "Golden" Safe Recipes
    # They must be verified and have exactly the core restrictions (or a superset)
    golden_1 = {
        "name": "Avocado Cacao Mousse",
        "servings": 20,
        "verified": True,
        "suitable_for": ["vegan", "peanut-allergy", "dairy-free", "gluten-free"],
        "ingredients": {"avocados": 4, "cacao powder (tbsp)": 10, "salt (tsp)": 0.5}
    }
    golden_2 = {
        "name": "Golden Lentil Stew",
        "servings": 10,
        "verified": True,
        "suitable_for": ["vegan", "peanut-allergy", "dairy-free", "gluten-free", "soy-free"], # Superset is valid
        "ingredients": {"lentils (cups)": 4, "broth (liters)": 2, "salt (tsp)": 2}
    }
    golden_3 = {
        "name": "Stuffed Bell Peppers",
        "servings": 5,
        "verified": True,
        "suitable_for": ["vegan", "peanut-allergy", "dairy-free", "gluten-free"],
        "ingredients": {"bell peppers": 5, "rice (cups)": 2, "salt (tsp)": 1}
    }

    with open("recipe_archive/desserts/golden_mousse.json", "w", encoding="utf-8") as f:
        json.dump(golden_1, f, indent=2)
    with open("recipe_archive/soups/golden_stew.json", "w", encoding="utf-8") as f:
        json.dump(golden_2, f, indent=2)
    with open("recipe_archive/mains/golden_peppers.json", "w", encoding="utf-8") as f:
        json.dump(golden_3, f, indent=2)

if __name__ == "__main__":
    build_env()
