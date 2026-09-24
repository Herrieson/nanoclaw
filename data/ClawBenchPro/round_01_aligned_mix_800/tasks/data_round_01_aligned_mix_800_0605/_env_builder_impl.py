import os

def build_env():
    # Create directories using relative paths (cwd is already assets/data_round_01_aligned_mix_800_0605/)
    os.makedirs('shop_notes', exist_ok=True)
    os.makedirs('office_reports', exist_ok=True)

    # Messy, informal mechanic logs mixed with personal details
    logs = {
        "monday.txt": "Man, Monday morning and I'm already exhausted. Did a full transmission rebuild on a '08 Silverado. Took me 12 hours straight. Used about 8 quarts of synthetic trans fluid. Boss is complaining about taxes again, like that's anything new. Can't wait for the weekend.",
        
        "tuesday.txt": "Just an engine oil change today on a Civic, took 1 hour, used 5 quarts of regular motor oil. The 4-year-old was driving me crazy last night, didn't get a wink of sleep. Need to get them out to the woods so they can burn off that energy.",
        
        "wednesday.txt": "Busy day today. Did a transmission flush on a Ford F-250. 2 hours of labor on that beast. Sucked up 14 quarts of trans fluid. Also spent 3 hours doing spark plugs on a Camry. Look, I'm telling you, people just don't take care of their cars anymore.",
        
        "thursday.txt": "Replacing a transmission solenoid on a Dodge Ram. Took 4 hours because the bolts were rusted tight. Lost some fluid when I dropped the pan, had to put in 3 quarts to top it off. Thinking about packing up the RV for Ocala tonight."
    }

    # Write logs to the shop_notes directory
    for filename, content in logs.items():
        with open(os.path.join('shop_notes', filename), 'w') as f:
            f.write(content)

if __name__ == '__main__':
    build_env()
