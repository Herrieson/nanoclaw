import os

def build_env():
    # Target directory for assets
    asset_dir = "assets/data_76"
    os.makedirs(asset_dir, exist_ok=True)

    # Chat history content based on persona
    chat_content = """
========================================
SYSTEM: Export initiated at 15:42:01
DEVICE: iPhone 11 (iOS 16.2)
========================================

[10:02 AM] Abuela: Mija, don't forget to study for your test! And clean your room, the craft supplies are everywhere.
[10:15 AM] Me: I know, I know. I'm working on the upcycled bracelets rn.
[11:00 AM] EcoJake: Yo, I secured 42 plastic bottles from the cafeteria recycling bins. They almost caught me lol.
[11:05 AM] Me: Bet! That's awesome for the upcycled planter project. We are saving the planet one bottle at a time! 🌍
[12:30 PM] CraftStoreBot: Your order for "Assorted Glass Beads (Earth Tones)" has shipped.
[01:00 PM] Mrs. G (Babysitting): Hi sweetie! Thanks for watching Tommy this week. Just to confirm my math, you did 3.5 hours on Monday, and 2 hours on Wednesday?
[01:05 PM] Me: Yes! And don't forget the 4 hours on Friday when you guys went to dinner. Rate is still $15/hr, right?
[01:10 PM] Mrs. G (Babysitting): Perfect, yes $15/hr. I'll venmo you tonight. Tommy says hi!
[01:12 PM] Me: Tell him I say hi! He was so good while we were painting.
[02:20 PM] Sarah_Green: hey bestie, I got 18 bottles. Leo totally flexed and brought 105!! He raided his dad's office lol.
[02:25 PM] Me: No cap Leo is insane. That's so good for the club.
[02:50 PM] RandomNumber: hey is this Maria? 
[02:51 PM] Me: who is this?
[03:00 PM] Maya_Eco: Sorry I'm late to the chat! I have 33 bottles cleaned and ready to go.
[03:05 PM] Me: Awesome Maya! 
========================================
END OF EXPORT
========================================
"""

    file_path = os.path.join(asset_dir, "chat_history_export.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(chat_content.strip())

    print(f"Environment built successfully in {asset_dir}")

if __name__ == "__main__":
    build_env()
