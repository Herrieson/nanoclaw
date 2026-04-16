import os

def build_env():
    base_dir = "assets/data_330"
    data_dir = os.path.join(base_dir, "community_data")
    os.makedirs(data_dir, exist_ok=True)

    chat1_content = """
[10:02 AM] Carlos: Hey everyone, it's Carlos! I play Indie Rock. Super excited for the showcase. You can reach me at carlos_rock at gmail dot com.
[10:15 AM] Luis: Luis here, doing some smooth jazz stuff. Can't wait. email: luis_jazz@yahoo.com
[10:30 AM] Hector: What's good? I do Heavy Metal. hector_metal@metal.org
"""
    
    chat2_content = """
[11:00 AM] Elena: Yo, Elena here. I'm bringing the Reggaeton vibes! Contact me: elena_reggaeton [at] outlook [dot] com.
[11:15 AM] Sofia: Sofia in the house. I play Classical piano. sofia.piano@edu.com
[11:45 AM] Mateo: Mateo here! I'm an Indie Rock guy too. Hit me up at mateo_indie AT protonmail DOT com.
"""

    with open(os.path.join(data_dir, "chat_logs_1.txt"), "w", encoding="utf-8") as f:
        f.write(chat1_content)
        
    with open(os.path.join(data_dir, "chat_logs_2.txt"), "w", encoding="utf-8") as f:
        f.write(chat2_content)

    venues_content = """Venue Name,Capacity,Area
The Basement,150,Downtown
Rooftop Lounge,200,Uptown
Jazz Corner,100,Midtown
Warehouse 9,500,Industrial District
"""
    with open(os.path.join(data_dir, "venues.csv"), "w", encoding="utf-8") as f:
        f.write(venues_content)

    # Corrupted JSON-like file
    corrupted_json_content = """{
    'Carlos': 'The Basement',
    'Luis': 'Jazz Corner',
    'Elena': 'Rooftop Lounge',
    'Mateo': 'Warehouse 9',
    'Hector': 'The Basement',
}
"""
    with open(os.path.join(data_dir, "artist_preferences.txt"), "w", encoding="utf-8") as f:
        f.write(corrupted_json_content)

if __name__ == "__main__":
    build_env()
