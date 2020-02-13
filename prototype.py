import requests
from bs4 import BeautifulSoup as soup

URL = 'https://en.wikipedia.org/wiki/Category:Iranian_Revolution'

# open connection and grab html
page_html = requests.get(URL).text

# parse html and extract links
page_soup = soup(page_html, "html.parser")
bod_soup = page_soup.find("div", {"id":"bodyContent"})

links = []
links_soup = bod_soup.findAll("a", {"href": lambda L: L and L.startswith("/wiki/")})
for ii in range(len(links_soup)):
    if not links_soup[ii]["href"].endswith(".jpg"):
        links.append(links_soup[ii]["href"]) # convert soup to string
    
for ii in range(len(links)):
    print(links[ii])