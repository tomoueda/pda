import urllib2
import fileinput
import re
from lxml import etree

#this corresponds to the main site we are scraping data off of.
#change if this link ever breaks.
domain = 'http://www.puzzledragonx.com/'
#this corresponds to the large dungeon list in puzzledragonx
#change is this link ever breaks.
start_domain = 'http://www.puzzledragonx.com/?dir=1'
grand_parties = {}
associated_parties = {}
non_decimal = re.compile(r'[^\d.]+')

def main():
    construct_grand_party_dict()
    print 'finished constructing grand party dictionary'
    for line in fileinput.input():
        line = non_decimal.sub('', line)
        monster_num = int(line)
        construct_associated(monster_num)

"""
This function creates dictionary where the key
is the dungeon and party are parties with only the associated monsters.
"""
def construct_associated(monster_num):
    for dungeon, parties in grand_parties.items():
        print dungeon
        asso_parties = get_assoc(monster_num, parties)
        associated_parties[dungeon] = asso_parties
        print '======================================='
        for party in asso_parties:
            for elem in party.iter():
                if 'href' in elem.attrib:
                    image = elem.find("img")
                    print image.attrib['title']
            print '========================'

"""
This is the reduce part of the map reduce.
Get only the parties that have monster_number
"""
def get_assoc(monster_num, parties):
    assoc_list = []
    for party in parties:
        for elem in party.iter():
            if 'href' in elem.attrib:
                target = elem.attrib['href']
                party_num = target[14:]
                party_num = non_decimal.sub('', party_num)
                party_num = int(party_num)
                if party_num == monster_num:
                    assoc_list.append(party)
                    break
    return assoc_list


"""
This function creates a large dictionary of dungeons and parties to
conquer that dungeon.
"""
def construct_grand_party_dict():
    response = urllib2.urlopen(start_domain)
    root = etree.parse(response, etree.HTMLParser())
    dungeon_urls = root.findall("//td[@class=\"dungeonname\"]/a")
    for url in dungeon_urls:
        print url.text
        str_url = domain + url.attrib["href"]
        response = urllib2.urlopen(str_url)
        droot = etree.parse(response, etree.HTMLParser())
        different_difficulties = droot.findall("//td[@class=\"title nowrap\"]/a")
        for durl in different_difficulties:
            print durl.text
            request =  domain + 'en/' + durl.attrib["href"]
            response = urllib2.urlopen(request)
            root_in = etree.parse(response, etree.HTMLParser())
            parties = root_in.findall("//td[@class=\"pt\"]/")
            grand_parties[durl.text] = parties
        parties = root.findall("//td[@class=\"pt\"]/")
        grand_parties[url.text] = parties

if __name__ == "__main__":
    main()
