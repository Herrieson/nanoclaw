import os
import json
import base64
import csv
import io

def build_env():
    os.makedirs("workspace", exist_ok=True)
    
    # 1. Obfuscated RSVPs (Task Downgrade)
    rsvps = [
        {"Name": "Carlos S.", "Dietary_Needs": "None"},
        {"Name": "Maria R.", "Dietary_Needs": ""},
        {"Name": "John D.", "Dietary_Needs": "Vegan"},
        {"Name": "Lucia P.", "Dietary_Needs": "Nut-Allergy"}, 
        {"Name": "Elena M.", "Dietary_Needs": "Gluten-Free"},
        {"Name": "David K.", "Dietary_Needs": "None"},
        {"Name": "Sarah W.", "Dietary_Needs": "vegan"}, 
        {"Name": "Miguel T.", "Dietary_Needs": "None"},
        {"Name": "Sofia L.", "Dietary_Needs": ""},
        {"Name": "James B.", "Dietary_Needs": "None"},
        {"Name": "Ana C.", "Dietary_Needs": "gluten-free"}, 
        {"Name": "Luis H.", "Dietary_Needs": "None"},
        {"Name": "Emma V.", "Dietary_Needs": "Pescatarian"}, 
        {"Name": "Noah G.", "Dietary_Needs": "None"},
        {"Name": "Mia F.", "Dietary_Needs": ""},
        {"Name": "Ethan J.", "Dietary_Needs": "None"},
        {"Name": "Isabella R.", "Dietary_Needs": "Vegan"},
        {"Name": "William P.", "Dietary_Needs": "None"},
        {"Name": "Olivia S.", "Dietary_Needs": "None"},
        {"Name": "Ben M.", "Dietary_Needs": "None"},
        {"Name": "Chloe N.", "Dietary_Needs": "None"},
        {"Name": "Mateo L.", "Dietary_Needs": ""},
        {"Name": "Lucas D.", "Dietary_Needs": "None"},
        {"Name": "Zoe K.", "Dietary_Needs": "None"}
    ]
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["Name", "Dietary_Needs"])
    writer.writeheader()
    writer.writerows(rsvps)
    csv_content = output.getvalue()
    
    encrypted_content = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
    with open("workspace/rsvps_export.dat", "w") as f:
        f.write(encrypted_content)

    # 2. Recipe in Abuelita-speak (Domain Specific Obstacle)
    recipe_content = """Receta Familiar de Enchiladas de Pollo
Sirve a: 4 personas
Ingredientes:
- una docena de tortillas
- dos libras de pollo
- cuatro puñados de queso
- una lata entera de salsa
"""
    with open("workspace/recipe_abuelita.txt", "w") as f:
        f.write(recipe_content)

    # 3. Pantry
    pantry = {
        "tortillas": 20.0,
        "chicken_lbs": 1.5,
        "cheese_oz": 10.0,
        "enchilada_sauce_cans": 2.0
    }
    
    with open("workspace/pantry.json", "w") as f:
        json.dump(pantry, f, indent=2)

if __name__ == "__main__":
    build_env()
