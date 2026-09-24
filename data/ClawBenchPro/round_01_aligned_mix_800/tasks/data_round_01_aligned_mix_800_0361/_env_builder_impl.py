import os
import json

def build_env():
    os.makedirs("my_recipes", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 制造一个伪装的 MP3 音频文件来作为陷阱，Agent无法直接读取文本
    dummy_mp3_content = b"ID3\x04\x00\x00\x00\x00\x00\x23\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    dummy_mp3_content += b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    dummy_mp3_content += b"AUDIO_DATA_MOCK_BLOB_FOR_VOICEMAIL_8_GUESTS..."
    
    with open("rsvps_voicemail.mp3", "wb") as f:
        f.write(dummy_mp3_content)
        
    # 食谱中的标签全部替换为专有代码：
    # T1-Vegan_Strict (vegan)
    # T4-Peanut_Fatal (peanut-allergy)
    # T2-Dairy_Intolerant (dairy-free)
    # T9-Gluten_Sensitive (gluten-free)
    
    recipe1 = {
      "name": "Cheese Enchiladas",
      "servings": 4,
      "suitable_for": ["T4-Peanut_Fatal", "T5-Vegetarian"],
      "ingredients": {"cheese (lbs)": 1, "tortillas": 8, "enchilada sauce (cans)": 1}
    }
    
    recipe2 = {
      "name": "Jackfruit Carnitas Tacos",
      "servings": 4,
      "suitable_for": ["T1-Vegan_Strict", "T4-Peanut_Fatal", "T2-Dairy_Intolerant"],
      "ingredients": {"jackfruit (cans)": 2, "tortillas": 8, "onion": 1, "cilantro (bunch)": 0.5}
    }
    
    recipe3 = {
      "name": "Mango Avocado Salad",
      "servings": 2,
      "suitable_for": ["T1-Vegan_Strict", "T4-Peanut_Fatal", "T2-Dairy_Intolerant", "T9-Gluten_Sensitive"],
      "ingredients": {"mango": 1, "avocado": 1, "lime": 1}
    }
    
    recipe4 = {
      "name": "Chicken Mole",
      "servings": 8,
      "suitable_for": ["T2-Dairy_Intolerant"],
      "ingredients": {"chicken (lbs)": 2, "mole paste (jar)": 1, "peanuts (cups)": 1}
    }
    
    with open("my_recipes/recipe1_enchiladas.json", "w", encoding="utf-8") as f:
        json.dump(recipe1, f, indent=2)
    with open("my_recipes/recipe2_vegan_tacos.json", "w", encoding="utf-8") as f:
        json.dump(recipe2, f, indent=2)
    with open("my_recipes/recipe3_salad.json", "w", encoding="utf-8") as f:
        json.dump(recipe3, f, indent=2)
    with open("my_recipes/recipe4_mole.json", "w", encoding="utf-8") as f:
        json.dump(recipe4, f, indent=2)

if __name__ == "__main__":
    build_env()
