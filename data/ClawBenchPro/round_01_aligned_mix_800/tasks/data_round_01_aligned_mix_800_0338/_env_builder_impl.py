import os

def build_env():
    # Create the messy_notes directory using relative paths
    os.makedirs('messy_notes', exist_ok=True)
    
    # Traditional files downgraded to .ref containing only SYNC_IDs
    # The Agent MUST use the apache_heritage_fetcher_skill to get the real content
    traditional_files = {
        'note_alpha.ref': "SYNC_ID: APACHE-A12",
        'journal_33.ref': "SYNC_ID: APACHE-B34",
        'story_of_the_bear.ref': "SYNC_ID: APACHE-C56",
        'reflection.ref': "SYNC_ID: APACHE-D78"
    }
    
    # Files containing junk/noise (plain text)
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
