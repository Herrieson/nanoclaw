import os

def build_env():
    # Create the messy_notes directory using relative paths
    os.makedirs('messy_notes', exist_ok=True)
    
    # Files containing traditional/Apache/family content
    traditional_files = {
        'note_alpha.txt': "The old ones used to say that peace is found in the stillness of the desert. Our Apache ancestors walked these lands with respect.",
        'journal_33.log': "Auntie's frybread recipe: 2 cups flour, 1 tablespoon baking powder, 1/2 teaspoon salt, 1 cup warm water. Fry in oil until golden. A simple tradition.",
        'story_of_the_bear.md': "My grandfather told me the story of the bear. He said it teaches us equality among all living creatures. We must preserve our heritage.",
        'reflection.txt': "Sitting by the window today. I prefer the solitude. Thinking about the traditional ceremonies back in Arizona."
    }
    
    # Files containing junk/noise
    junk_files = {
        'math_hw_final.txt': "Algebra 1, Grade 9. Solve for x: 3x + 5 = 20. x = 5. I hate math.",
        'game_strats.md': "Fortnite drop locations: Always drop at tilted towers. Get the legendary loot and build 90s.",
        'random_jokes.log': "Why did the chicken cross the road? To get to the other side! LOL.",
        'shopping_list.txt': "Doritos, Mountain Dew, Xbox gift card, hot pockets.",
        'sys_error_881.log': "ERROR 0x80070057: The parameter is incorrect. Memory dump initiated.",
        'todo_weekend.txt': "1. Beat the new boss in Elden Ring. 2. Sleep until noon. 3. Avoid homework."
    }
    
    # Write files to the messy_notes directory
    for filename, content in traditional_files.items():
        with open(os.path.join('messy_notes', filename), 'w', encoding='utf-8') as f:
            f.write(content)
            
    for filename, content in junk_files.items():
        with open(os.path.join('messy_notes', filename), 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == '__main__':
    build_env()
