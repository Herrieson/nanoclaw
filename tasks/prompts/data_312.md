Hello there. *adjusts glasses* I'm in a bit of a bind today. Between getting the kids ready this morning and preparing for my upcoming graduate seminar on 19th-Century Industrial Literature, I am feeling quite overwhelmed. 

My research assistant downloaded a batch of public domain texts for me, but the files are a complete mess. I placed them in the `literature_raw` folder in my workspace. I need you to handle two things for me so I can focus on my lecture notes:

First, there are some glaring OCR errors that will distract my students. In all the text files, the word "the" is frequently misspelled as "teh", and "which" is misspelled as "whcih". Please fix these errors in the texts (ensure you preserve the original capitalization if possible, though mostly it's lowercase 'teh' and 'whcih'). Save all the corrected text files into a new folder named `cleaned_texts` in my workspace.

Second, I need a quantitative thematic analysis for my presentation. Please generate a file named `theme_analysis.csv` in the root of my workspace. The CSV must have exactly these columns: `Title`, `Author`, `Nature_Count`, `Industry_Count`.
- The `Title` is always located on the first line of the raw file, formatted like "Title: [Actual Title]".
- The `Author` is always on the second line, formatted like "Author: [Actual Author]".
- `Nature_Count` should be the total number of times any of these words appear in the text: 'river', 'tree', 'bird', 'nature'.
- `Industry_Count` should be the total number of times any of these words appear in the text: 'machine', 'factory', 'engine', 'smoke'.
*(Note: Please count these as whole words only, and the counting should be case-insensitive).*

Thank you so much for your help. I really need this properly formatted before I have to leave to pick up my 4-year-old from preschool.
