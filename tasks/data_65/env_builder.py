import os
import base64

def build_env():
    base_dir = "assets/data_65"
    drafts_dir = os.path.join(base_dir, "drafts")
    
    os.makedirs(drafts_dir, exist_ok=True)
    
    # Define the files and their original content
    files_data = {
        "entry_20231001.txt": "Title: The Autumn Leaves\n\nThey fall so quietly,\nLike a whisper in the wind.\nI watch them from my window,\nWaiting for winter to begin.\n",
        "entry_20231005.txt": "Dear diary,\nToday was just okay. I sat in the back of math class and read a book. I hope nobody noticed me fidgeting during the pop quiz.\n",
        "entry_20231012.txt": "Just a quick note to myself: remember to buy more pencils. Also, I need to finish that history essay by Friday.\n",
        "entry_20231015.txt": "Title: My Quiet Room\n\nIn the silence of the afternoon,\nMy corazon beats a steady tune.\nAway from the noise, away from the crowd,\nWhere thoughts can breathe and not be loud.\n",
        "entry_20231020.txt": "Title: Shadows on the Wall\n\nThey dance and play when the sun goes down,\nDrawing shapes of a sleepy town.\nA secret world just for me,\nWhere I can close my eyes and just be.\n",
        "entry_20231025.txt": "Title: The Blank Page\n\nStaring at the paper white,\nTrying to find the words to write.\nA piece of my corazon on display,\nHoping the fear will wash away.\n"
    }
    
    # Write encoded content to the files
    for filename, content in files_data.items():
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        file_path = os.path.join(drafts_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(encoded_content)

if __name__ == "__main__":
    build_env()
