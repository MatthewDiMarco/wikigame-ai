import sys
import random
import traceback
import difflib as dl
import requests as req
from bs4 import BeautifulSoup as soup
from nltk.corpus import wordnet
from numpy import exp
import numpy as np

# constants
TURNS = 50
SYNTAX = 'USAGE: python wikigame_bot.py <start_url> <target_url>'
WIKIPEDIA = 'https://en.wikipedia.org'

def main():
    try:
        if not len(sys.argv) == 3:
            raise ValueError("Recieved {} arguments: expected 2\n{}".format(
                len(sys.argv) - 1, SYNTAX
            ))
        else:
            start_page = Page(sys.argv[1])
            target_page = Page(sys.argv[2])
            
            print("validating pages...\n")
            if not start_page.exists():
                raise ValueError("{} does not exist".format(start_page.url))
            elif not target_page.exists():
                raise ValueError("{} does not exist".format(target_page.url))
            else:
                
                # start main loop (play game)
                target_name = target_page.get_name()
                counter = TURNS
                curr_page = start_page
                while (not curr_page.url == target_page.url) and (counter > 0):
                    print("reading...")
                    successor_link = curr_page.analyse_links(target_name)
                    print("moving to... {}".format(successor_link))
                    curr_page = Page(successor_link)
                    counter = counter - 1
                    
                if counter > 0:
                    print("Bot wins!")
                else:
                    print("Bot fails: No turns remain...")
                                
    except (ValueError, IndexError) as e:
        print("---ERROR---\n{}".format(e))
        print(traceback.print_exc())

class Page:
    def __init__(self, in_url):        
        self.url = ''.join((WIKIPEDIA, '/wiki/', in_url))
        
    def exists(self):
        '''
        Returns true if the url is a real article.
        Should call after construction if unsure of article validity
        '''
        exists = True
        msg = "Wikipedia does not have an article with this exact name."
        
        body = self.__get_body()
        infobox = body.find("td", {"class":"mbox-text"})
        if not infobox is None:
            btag_list = infobox.findAll("b")
            if len(btag_list) > 1 and btag_list[1].text == msg:
                exists = False
        
        return exists
                
    def analyse_links(self, target):
        '''Return link with highest % similarity score to the target str'''
        links = self.__scrape_links()
        best_link = (0,0) # tuple for tracking best link: (index,score)
        for ii in range(len(links)):
            
            name1,name2 = links[ii].split('/')[2],target.split('/')[2]
            score = self.similarity(name1, name2) 
    
            # guesstimate the best link by adding some randomness
            margin = 0.1 * score
            score += random.uniform(-margin, margin)
            
            if score > best_link[1]:
                best_link = (ii,score)
        
        print(best_link[1])
        return links[best_link[0]].split('/')[2]
    
    def get_name(self):
        '''Returns url in /wiki/name format'''
        fragments = self.url.split("/")
        return ''.join(("/wiki/", fragments[4]))
    
    def display(self):
        print("This page: {}".format(self.url))
        links = self.__scrape_links()
        for ii in range(len(links)):
            print(links[ii])
    
    # NOTE: Remember you need to download nltk (it's a dependency)
    def similarity(self, str1, str2):
        '''n/a'''
        
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
                        except Exception as e: #TODO: FIX EXCEPTIONS!! >:(
                            pass
                except Exception as e:
                    pass # go to next word
            
        return best_confidence
        '''     
        confidence = 0
        if str1.lower() == str2.lower():
            confidence = 100
        else:
            str1_words = str1.lower().split('_')
            str2_words = str2.lower().split('_')
            
            for word_ii in range(len(str1_words)):
                related_words_ii = 
                for word_jj in range(len(str2_words)):
        '''
        
    def normalise(self, x, lower, upper):
        '''
        Normalisation function. 
        Crunches any real number (x) in-between the range 'upper' and 'lower' (e.g. 0 and 1).
        '''
        return (upper - lower) / (1 + exp(-x)) + lower

             
    # important!! VV       
    # https://pythonprogramming.net/wordnet-nltk-tutorial/  
    # if keywords are identified, return 100%!! (parse at _ ?)
    # remove case sensitivity
    def similarity_old(self, str1, str2):
        '''Returns the % similarity between two strings'''
        if str1.lower() == str2.lower():
            similarity = 101
        else:
            def splt(str):
                return (str.lower()).split('_')
            
            str1_words = splt(str1)
            str2_words = splt(str2)
            
            keyword_found = False
            for ii in range(len(str1_words)):
                for jj in range(len(str2_words)):
                    if str1_words[ii] == str2_words[jj]:
                        keyword_found = True
            
            if keyword_found == False:
                similarity = dl.SequenceMatcher(None, str1, str2).ratio() * 100
            else:
                similarity = 100
            
        return similarity
    
    def __scrape_links(self):
        '''Returns a list of wiki articles on this url'''
        links = []
        bod_soup = self.__get_body()        
        links_soup = bod_soup.findAll("a", {
            "href": lambda L: L and L.startswith("/wiki/")
        })
        
        for ii in range(len(links_soup)):
            if (not links_soup[ii]["href"].endswith(".jpg")) and (
                not links_soup[ii]["href"].endswith(".png")) and (
                not len(links_soup[ii]["href"]) > 30
            ):
                links.append(links_soup[ii]["href"]) # convert soup to string
                
        return links
    
    def __get_body(self):
        page_html = req.get(self.url).text
        page_soup = soup(page_html, "html.parser")
        return page_soup.find("div", {"id":"bodyContent"})

if __name__ == "__main__":
    main()