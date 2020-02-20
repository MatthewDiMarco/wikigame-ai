# wikigame-ai
This is a short python script I wrote up briefly as a fun side project.

The goal was to create a bot/ai that could play the [wikigame](https://www.thewikigame.com/group) faster than a human could. This is not the same as a bot that plays the game more efficiently, or a bot that finds the shortest path between two articles. This is by no means the best attempt at a wikigame ai, but simply my best attempt as a personal challenge.

# Usage
```
python wikigame_bot.py <start_page> <target_page>
```
Please note that <start_page> and <target_page> are the article names, NOT the URLs. The script will validate the articles automatically before commencing the game. For example:
```
python wikigame_bot.py The_Doors Mathematics

validating articles...
https://en.wikipedia.org/wiki/The_Doors... VALID
https://en.wikipedia.org/wiki/Mathematics... VALID

moving to... The_Doors_Classics
moving to... Template_talk:The_Doors
moving to... Music_genre
moving to... Music_psychology
moving to... Affective_science
moving to... Political_science
moving to... Social_science
moving to... Mathematics
Bot wins!
Time:  8.6942 seconds
Steps: 8 clicks
```
Also note that article names are treated non case sensitive.

# Dependencies
With pip, install: beautifulsoup4, requests and nltk
Then run:
```
import nltk
nltk.download() 
```
After this, the script should be ready to go.

# How it works
Once the start and target pages have been defined, the following algorithm starts:
1. Scrape all the links from the current page and put them in a list.
2. For each link: Use the Wu-Palmer Semantic Similarity method from the nltk wordnet import to find keywords between the current article name and the target article name. Additionally, throw in a + or - 5% randomness to the score to help the bot avoid getting stuck in loops.
3. If we found a link in the list that is an exact match to the target link, then the game ends. Else, repeat steps 1 with the best link the bot could find until the bot wins or runs out of turns.
