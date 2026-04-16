import os

def create_diary():
    target_dir = "assets/data_435"
    os.makedirs(target_dir, exist_ok=True)
    
    diary_content = """
    April 12th:
    Ahhhh I just finished reading *Into the Wild* and I am sobbing! 😭 The wilderness is so beautiful but so unforgiving. I really want to hike near there someday, though maybe safely! 
    Dream hike location: 63.8684, -149.0494. It's going to be freezing but I have to go!

    April 15th:
    Okay, wow. *Wild: From Lost to Found* is literally my new personality. Cheryl Strayed is amazing. I need to hike the PCT. I found a section near Mt. Hood that looks gorgeous!
    Dream hike location: 45° 22' 10" N, 121° 41' 40" W. I already started looking at new hiking boots.

    April 22nd:
    Just finished *A Walk in the Woods*. Bill Bryson makes the Appalachian Trail sound terrifying but hilarious. I'm adding a spot in the Smokies to my list.
    Dream hike location: 35.5628, -83.4985. I hope I don't run into any bears!!! 🐻

    May 1st:
    *Touching the Void* was INTENSE. I couldn't put it down. I don't think I'll ever do hardcore mountaineering, but I'd love to hike the Siula Grande base camp area in Peru.
    Dream hike location: 10° 16' 30" S, 76° 54' 0" W. So far from home!

    May 5th:
    Read a classic today! *The Call of the Wild*! Buck's journey is so emotional. I'd love to see the Yukon River.
    Dream hike location: 60° 43' 59" N, 135° 3' 2" W. I definitely need to upgrade my winter gear before I even think about this one.
    """
    
    with open(os.path.join(target_dir, "my_messy_diary.txt"), "w", encoding="utf-8") as f:
        f.write(diary_content.strip())

if __name__ == "__main__":
    create_diary()
