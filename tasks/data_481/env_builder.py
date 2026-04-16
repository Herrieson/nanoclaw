import os

def build_env():
    base_dir = "assets/data_481"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create the messy HTML blog dump
    html_content = """
    <html>
    <head><title>Aussie Indie Beats & Pieces</title></head>
    <body>
        <h1>Late Night Finds</h1>
        <div class="review">
            <h2><span class="artist">Neon Monks</span> - <span class="track">Silent Choirs</span></h2>
            <p class="desc">A highly ethereal track with heavy synth backing. Really takes you to another dimension.</p>
        </div>
        <div class="review">
            <h2><span class="artist">Grungy Pete</span> - <span class="track">Muddy Boots</span></h2>
            <p class="desc">Just some loud noisy rock. Nothing special, very abrasive and loud.</p>
        </div>
        <div class="review">
            <h2><span class="artist">The Burnt Toast</span> - <span class="track">Morning Routine</span></h2>
            <p class="desc">It has a deeply nostalgic feel from the 80s. Makes me think of my childhood in Sydney.</p>
        </div>
        <div class="review">
            <h2><span class="artist">Echo Chamber</span> - <span class="track">Vastness</span></h2>
            <p class="desc">Ambient sounds. Too slow for dancing, but good for sleeping.</p>
        </div>
        <div class="review">
            <h2><span class="artist">Crimson Rebels</span> - <span class="track">System Shock</span></h2>
            <p class="desc">A rebellious anthem for the modern age. Guitars are completely out of control.</p>
        </div>
        <div class="review">
            <h2><span class="artist">DJ Sleep</span> - <span class="track">Lullaby 04</span></h2>
            <p class="desc">Extremely boring. No redeeming qualities.</p>
        </div>
    </body>
    </html>
    """
    with open(os.path.join(base_dir, "blog_dump.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    # 2. Create the agency vibes keyword file
    vibes_content = "ethereal\nnostalgic\nrebellious\n"
    with open(os.path.join(base_dir, "agency_vibes.txt"), "w", encoding="utf-8") as f:
        f.write(vibes_content)

    # 3. Create the mock local tool for fetching ISRC codes
    mock_db_script = """#!/usr/bin/env python3
import sys
import hashlib

def get_isrc(query):
    # Mock database lookup logic using a hash to be deterministic but opaque
    known_db = {
        "Neon Monks - Silent Choirs": "AU-NM1-23-0001",
        "Grungy Pete - Muddy Boots": "AU-GP2-23-0002",
        "The Burnt Toast - Morning Routine": "AU-BT3-23-0003",
        "Echo Chamber - Vastness": "AU-EC4-23-0004",
        "Crimson Rebels - System Shock": "AU-CR5-23-0005",
        "DJ Sleep - Lullaby 04": "AU-DS6-23-0006"
    }
    
    if query in known_db:
        return known_db[query]
    
    # Fallback deterministic generator
    h = hashlib.md5(query.encode()).hexdigest()[:8].upper()
    return f"XX-XXX-23-{h}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python music_db.py \\"Artist - Track\\"")
        sys.exit(1)
    
    query = sys.argv[1].strip()
    print(get_isrc(query))
"""
    db_script_path = os.path.join(base_dir, "music_db.py")
    with open(db_script_path, "w", encoding="utf-8") as f:
        f.write(mock_db_script)
    os.chmod(db_script_path, 0o755)

if __name__ == "__main__":
    build_env()
