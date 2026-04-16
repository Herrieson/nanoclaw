import os

def build_env():
    base_dir = "assets/data_130"
    os.makedirs(base_dir, exist_ok=True)

    rsvps_content = """# System Export: CommunityPortal v2.1.4
# Note: Format errors detected during export.
Name|RSVP|Film Preference|Dietary Needs
Alice Johnson|Yes|Modern Times|Vegan
Bob Smith;No;The Kid;None
Charlie Davis|Yes|Modern Times|Gluten-Free, Peanut Allergy
Diana Prince,Maybe,City Lights,Vegetarian
Evan Wright|Yes|City Lights|lactose intolerant
Fiona Gallagher;Yes;Modern Times;Vegan
George Miller|Yes|City Lights|None
Hannah Abbott,Yes,Modern Times,Peanut Allergy
Ian Malcolm|No|Jurassic Park|Carnivore
Jenny Slate;Yes;The Great Dictator;Gluten-Free, dairy free
Kevin Hart|Yes|Modern Times|
Laura Dern,Yes,City Lights,vegan
"""
    
    with open(os.path.join(base_dir, "raw_rsvps.txt"), "w", encoding="utf-8") as f:
        f.write(rsvps_content)

if __name__ == "__main__":
    build_env()
