import sys
import random
import time
import requests as req
from bs4 import BeautifulSoup as soup
from nltk.corpus import wordnet

# constants
CRED = '\033[91m' #red
CGRE = '\33[32m' #green
CEND = '\033[0m' #def
TURNS = 50
HTTPS = 'https://en.wikipedia.org/wiki/'
SYNTAX = (
    'USAGE: python wikigame_bot.py <start_url> <target_url>'
) 

def main():
    try:
        if not len(sys.argv) == 3:
            raise ValueError("Recieved {} arguments: expected 2\n{}".format(
                len(sys.argv) - 1, SYNTAX
            ))
        else:
            # load articles
            start_page = Page(sys.argv[1])
            target_page = Page(sys.argv[2])
            
            # validate articles
            print("validating articles...")
            sys.stdout.write("{}... ".format(start_page.url))
            if not start_page.exists():
                print(CRED + "FAIL" + CEND)
                raise ValueError("'{}' does not exist".format(start_page.url))
            print(CGRE + "VALID" + CEND)
            
            sys.stdout.write("{}... ".format(target_page.url))
            if not target_page.exists():
                print(CRED + "FAIL" + CEND)
                raise ValueError("'{}' does not exist".format(target_page.url))
            print(CGRE + "VALID" + CEND + "\n")
            
            # if no exceptions are thrown, start main loop (play game)
            bot = Bot(target_page)    
            counter = TURNS    
            curr_page = start_page
            
            start_seconds = time.time() # start timer
            while (not curr_page.url.lower() == target_page.url.lower()) and (counter > 0):
                successor_link = bot.read(curr_page)
                print("moving to... {}".format(successor_link))
                bot.clicks += 1
                curr_page = Page(successor_link)
                counter = counter - 1
                
            playtime = round(time.time() - start_seconds, 4) # stop timer
            if counter > 0:
                print(CGRE + "Bot wins!" + CEND)
            else:
                print(CRED + "Bot fails: No turns remain..." + CEND)
                
            print("Time:  {} seconds".format(playtime))
            print("Steps: {} clicks".format(bot.clicks))
                                
    except (ValueError, IndexError) as e:
        print(CRED + "{}".format(e) + CEND)

class Bot:
    def __init__(self, target_page):
        """Memory: list for tracking visited pages."""
        self.clicks = 0
        self.target = target_page
        self.memory = []
        
    def read(self, article):
        """
        Analyse links for keywords.
        Return link with best confidence.
        """
        self.memory.append(article.get_name().lower())
        
        target = self.target.get_name()
        links_ranked = []
        best_link = ''
        
        # sort links by confidence
        links = article.scrape_links()
        for ii in range(len(links)):
            if links[ii].lower == target.lower():
                return links[ii]
            else:
                links_ranked.append((links[ii], self.__confidence(links[ii], target)))
            
        links_ranked.sort(key=lambda elem: elem[1], reverse=True)

        # return top element unless bot has already visited the article (memory)
        ii,length = 0,len(links_ranked)
        best_link = ''
        searching = True
        while searching:
            best_link = links_ranked[ii][0]
            if best_link.lower() not in self.memory or ii >= length:
                searching = False
            ii = ii + 1
        
        return best_link
    
    def __confidence(self, str1, str2):
        """
        Returns the bot's 'confidence' in an article as a decimal between 0 and 1.
        Achieved by splitting up strings into words and analysing each word
        independantly to uncover keywords.
        """   
        best_confidence = 0
        syns = wordnet.synsets("program")
        str1_words = str1.lower().split('_')
        str2_words = str2.lower().split('_')
        
        for ii in range(len(str1_words)):
            try:
                word1 = wordnet.synset(''.join((str1_words[ii], '.n.01')))
                for jj in range(len(str2_words)):
                    try:
                        word2 = wordnet.synset(''.join((str2_words[jj], '.n.01')))
                        confidence = word1.wup_similarity(word2)
                        
                        if confidence > best_confidence:
                            best_confidence = confidence
                            
                    except Exception as e:
                        #for WordNetError exceptions
                        #If word couldn't be found, skip to next word
                        pass
                    
            except Exception as e:
                #for WordNetError exceptions
                #If word couldn't be found, skip to next word
                pass
            
        return best_confidence

class Page:
    def __init__(self, name):        
        self.url = ''.join((HTTPS, name))
        
    def exists(self):
        """Returns true if the url is a real article."""
        exists = True
        msg = (
            'Wikipedia does not have an article with this exact name.'
        )
        
        body = self.__get_body()
        infobox = body.find("td", {"class":"mbox-text"})
        
        if not infobox is None:
            btag_list = infobox.findAll("b")
            
            if len(btag_list) > 1 and btag_list[1].text == msg:
                exists = False
        
        return exists
    
    def scrape_links(self):
        """Returns a list of article links within this body's article"""
        bod_soup = self.__get_body()       
        links_soup = bod_soup.findAll("a", {
            "href": lambda L: L and L.startswith("/wiki/")
        })
        
        links = []
        for ii in range(len(links_soup)):
            if (  
                not links_soup[ii]["href"].lower().endswith(".jpg") and \
                not links_soup[ii]["href"].lower().endswith(".png") and \
                not len(links_soup[ii]["href"]) > 40
            ): 
                # convert soup to string and take just the name (dump '/wiki/')
                links.append(links_soup[ii]["href"].split("/")[2])
                
        return links
    
    def get_name(self):
        """Returns the name of the article without the url"""
        return self.url.split("/")[4]
    
    def __get_body(self):
        """Returns the body content of an article as a soup obj"""
        page_html = req.get(self.url).text
        page_soup = soup(page_html, "html.parser")
        return page_soup.find("div", {"id":"bodyContent"})

if __name__ == "__main__":
    main()