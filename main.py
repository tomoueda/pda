import urllib2
from lxml import etree

domain = 'http://www.puzzledragonx.com/'
grand_parties = {}

def main():
    construct_grand_party_list()
    print grand_parties

"""
This function creates a large dictionary of dungeons and parties to
conquer that dungeon.
"""
def construct_grand_party_list():
    response = urllib2.urlopen('http://www.puzzledragonx.com/?dir=1')
    root = etree.parse(response, etree.HTMLParser())
    dungeon_urls = root.findall("//td[@class=\"dungeonname\"]/a")
    for url in dungeon_urls:
        str_url = domain + url.attrib["href"]
        response = urllib2.urlopen(str_url)
        root = etree.parse(response, etree.HTMLParser())
        different_difficulties = root.findall("//table[@id=\"tablestat\"]/a")
        for durl in different_difficulties:
            response = urllib2.urlopen(domain + durl.attrib["href"])
            root_in = etree.parse(response, etree.HTMLParser())
            parties = root_in.findall("//td[@class=\"pt\"]/")
            grand_parties[durl.text] = parties
        parties = root.findall("//td[@class=\"pt\"]/")
        grand_parties[url.text] = parties

if __name__ == "__main__":
    main()
