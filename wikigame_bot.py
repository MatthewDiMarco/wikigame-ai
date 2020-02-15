import sys
import random
import time
import traceback
import requests as req
from bs4 import BeautifulSoup as soup
from nltk.corpus import wordnet

# constants
CRED = '\033[91m' #red
CGRE = '\33[32m' #green
CEND = '\033[0m' #def
TURNS = 50
WIKIPEDIA = 'https://en.wikipedia.org/wiki/'
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
            target_name = target_page.get_name()
            counter = TURNS
            curr_page = start_page
            
            start_seconds = time.time() # start timer
            while (not curr_page.url == target_page.url) and (counter > 0):
                successor_link = curr_page.analyse_links(target_name)
                print("moving to... {}".format(successor_link))
                curr_page = Page(successor_link)
                counter = counter - 1
                
            playtime = round(time.time() - start_seconds, 4) # stop timer
            if counter > 0:
                print(CGRE + "Bot wins!" + CEND)
            else:
                print(CRED + "Bot fails: No turns remain..." + CEND)
                
            print("Time: {} seconds".format(playtime))
                                
    except (ValueError, IndexError) as e:
        print(CRED + "{}".format(e) + CEND)
        #print(traceback.print_exc())

class Page:
    def __init__(self, in_url):        
        self.url = ''.join((WIKIPEDIA, in_url))
        
    def exists(self):
        """
        Returns true if the url is a real article.
        Should call after construction if unsure of article validity.
        """
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
                
    def analyse_links(self, target):
        """Returns article with highest % similarity score to the target article"""
        links = self.__scrape_links()
        best_article = (0,0) # tuple for tracking best link: (index,score)
        
        for ii in range(len(links)):
            score = self.__similarity(links[ii], target) 
    
            # guesstimate (i.e. add x% randomness to link selection to avoid infinite loops)
            PERCENT_VARIANCE = 10 #%
            margin = (PERCENT_VARIANCE / 100) * score
            score += random.uniform(-margin, margin)
            
            if score > best_article[1]:
                best_article = (ii,score)
        
        return links[best_article[0]]
    
    def get_name(self):
        """Returns the name of the article without the url"""
        return self.url.split("/")[4]
    
    def display(self):
        """Print out this page's url plus all it's links"""
        print("This page: {}".format(self.url))
        links = self.__scrape_links()
        for ii in range(len(links)):
            print(links[ii])
    
    ##
    # PRIVATES
    ##
    
    def __similarity(self, str1, str2):
        """
        Returns the similarity between 2 strings as a decimal between 0 and 1.
        
        Method: 1. Break each string up into a list of words (split @ '_' symbol).
                2. Do a cross-product comparison of each word from each list using
                   'Lemmatisation' to calculate the similarity between the 2 words.
                3. Out of all the comparisons, the highest calculated value will
                   be returned (pick out the keywords).
                   
        Dependencies: nltk.corpus - wordnet
        For this bot to work, run the following:
            >>> import nltk
            >>> nltk.download() 
        """   
        best_confidence = 0
        if str1.lower() == str2.lower():
            best_confidence = 1.0
        else:
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
    
    def __scrape_links(self):
        """Returns a list of article links within this body's article"""
        bod_soup = self.__get_body()       
        links_soup = bod_soup.findAll("a", {
            "href": lambda L: L and L.startswith("/wiki/")
        })
        
        links = []
        for ii in range(len(links_soup)):
            if (  
                not links_soup[ii]["href"].endswith(".jpg") and \
                not links_soup[ii]["href"].endswith(".png") and \
                not len(links_soup[ii]["href"]) > 30 #TODO: consider changing this...
            ): 
                # convert soup to string and take just the name (dump '/wiki/')
                links.append(links_soup[ii]["href"].split("/")[2])
                
        return links
    
    def __get_body(self):
        """Returns the body content of an article as a soup obj"""
        page_html = req.get(self.url).text
        page_soup = soup(page_html, "html.parser")
        return page_soup.find("div", {"id":"bodyContent"})

if __name__ == "__main__":
    main()