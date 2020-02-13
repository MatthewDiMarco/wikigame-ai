import sys
import random
import traceback
import difflib as dl
import requests as req
from bs4 import BeautifulSoup as soup

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
                    curr_page.scrape_links()
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
        if not in_url.startswith(WIKIPEDIA):
            raise ValueError("Invalid URL: must be a wiki page")
        else:                
            self.url = in_url
            self.links = []
        
    def scrape_links(self):
        '''Populate object list with valid wiki urls'''
        if len(self.links) > 0: # reset list if rescraping
            self.links = []
    
        bod_soup = self.__get_body()        
        links_soup = bod_soup.findAll("a", {
            "href": lambda L: L and L.startswith("/wiki/")
        })
        
        for ii in range(len(links_soup)):
            if not links_soup[ii]["href"].endswith(".jpg"):
                self.links.append(links_soup[ii]["href"]) # convert soup to string
                
    def analyse_links(self, target):
        '''Return link with highest % similarity score to the target str'''
        best_link = (0,0) # tuple for tracking best link: (index,score)
        for ii in range(len(self.links)):
            
            # compare just the page name - delete the '/wiki/'
            name1,name2 = self.links[ii].split("/")[1],target.split("/")[1]
            score = self.similarity(name1, name2)
            
            # guesstimate the best link by adding some randomness
            margin = 0.2 * score
            score += random.uniform(-margin, margin)
            
            if score > best_link[1]:
                best_link = (ii,score)
        
        print(best_link[1])
        return ''.join((WIKIPEDIA, self.links[best_link[0]]))
    
    def exists(self):
        '''Returns true if the url is a real article'''
        exists = True
        msg = "Wikipedia does not have an article with this exact name."
        
        body = self.__get_body()
        infobox = body.find("td", {"class":"mbox-text"})
        if not infobox is None:
            btag_list = infobox.findAll("b")
            if len(btag_list) > 1 and btag_list[1].text == msg:
                exists = False
        
        return exists
    
    def get_name(self):
        '''Returns url in /wiki/name format'''
        fragments = self.url.split("/")
        return ''.join(("/wiki/", fragments[4]))
    
    def display(self):
        print("This page: {}".format(self.url))
        for ii in range(len(self.links)):
            print(self.links[ii])
            
    # if keywords are identified, return 100%!! (parse at _ ?)
    # remove case sensitivity
    def similarity(self, str1, str2):
        '''Returns the % similarity between two strings'''
        
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
    
    def __get_body(self):
        page_html = req.get(self.url).text
        page_soup = soup(page_html, "html.parser")
        return page_soup.find("div", {"id":"bodyContent"})

if __name__ == "__main__":
    main()