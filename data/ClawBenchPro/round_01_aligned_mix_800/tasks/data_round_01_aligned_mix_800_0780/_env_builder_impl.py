import os

def build_env():
    os.makedirs("event_notes", exist_ok=True)
    
    files_content = {
        "day1_scraps.txt": "Ugh, the kids were acting up today. Anyway. Tom bought a pie, paid in cash. I heard a Black-capped Chickadee (chick-a-dee-dee-dee) near the feeder. Sarah owes me $15.00 for the vegan wraps. Need to restock flour at the store tomorrow.",
        "napkin_notes.txt": "John grabbed some sodas and chips, ran off without paying. Unpaid: $22.50. Saw a robin but didn't hear it. Wait, heard a Blue Jay (jay-jay) in the big oak while I was carrying the ice cooler.",
        "receipt_back.txt": "Alice owes $8.00 for the cookies. Heard an Eastern Towhee (drink-your-tea) while serving the birders. My knee is acting up again, need to sit down.",
        "phone_memo.txt": "Paid: Mark ($10). Unpaid: Dave ($12.00). Woodpecker drumming, but not a vocal call. Oh, heard a Northern Cardinal (cheer-cheer-cheer) right before closing up."
    }
    
    for fname, content in files_content.items():
        file_path = os.path.join("event_notes", fname)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    build_env()
