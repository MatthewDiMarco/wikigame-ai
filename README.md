# wikigame-ai
This is a short python script I wrote up briefly as a fun side project.

The goal was to create a bot/ai that could play the [wikigame](https://www.thewikigame.com/group) faster than a human could. This is not the same as a bot that plays the game more efficiently, or a bot that finds the shortest path between two articles. This is by no means the best attempt at a wikigame ai, but simply my best attempt as a personal challenge.

# Usage
```
python wikigame_bot.py <start_page> <target_page>
```
Please note that <start_page> and <target_page> are the article names, not the URLs. The script will validate the articles automatically before commencing the game. For example:
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
