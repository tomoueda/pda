import urllib2
import fileinput
import re
import json
import operator
from lxml import etree
from pdaclasses import *

#this corresponds to the main site we are scraping data off of.
#change if this link ever breaks.
domain = 'http://www.puzzledragonx.com/'
#this corresponds to the large dungeon list in puzzledragonx
#change is this link ever breaks.
start_domain = 'http://www.puzzledragonx.com/?dir=1'
grand_parties = {}
associated_parties = {}
mainbank = MonsterBank()
non_decimal = re.compile(r'[^\d]+')


def main():
    dungeon_urls = get_dungeon_urls()
    construct_bank(dungeon_urls)
    serialize_bank()
    # print 'please enter a monster number'
    # for line in fileinput.input():
    #     line = non_decimal.sub('', line)
    #     monster_num = int(line)
    #     monster = MonsterData(monster_num)
    #     find_associations(dungeon_urls, monster)
    #     print monster
    #     serialize(monster)

def serialize_bank():
    data = json.dumps(mainbank, cls=MonsterBankEncoder)
    with open('maindata.json', 'w') as outfile:
        json.dump(data, outfile)
    for key, monster in mainbank.bank.items():
        serialize(monster)


"""
Create the monster bank dictionary.
"""
def construct_bank(dungeon_urls):
    counter = 1
    for url in dungeon_urls:
        print str(float(counter) / len(dungeon_urls)) , 'progress'
        str_url = domain + url.attrib["href"]
        response = urllib2.urlopen(str_url)
        root = etree.parse(response, etree.HTMLParser())
        different_difficulties = root.findall("//td[@class=\"title nowrap\"]/a")
        update_bank(root, url)
        for durl in different_difficulties:
            request =  domain + 'en/' + durl.attrib["href"]
            response = urllib2.urlopen(request)
            root_in = etree.parse(response, etree.HTMLParser())
            update_bank(root_in, durl)
        counter += 1

"""
Serialize monsters in to a json file.
"""
def serialize(monster):
    data = json.dumps(monster, cls=MonsterDataEncoder)
    with open('monster_data/' + str(monster.monster_num) + '.json', 'w') as outfile:
        json.dump(data, outfile)

"""
Given a list of dungeon urls and a monster number
we could find all the parties this monster is in.
"""
def find_associations(dungeon_urls, monster):
    for url in dungeon_urls:
        str_url = domain + url.attrib["href"]
        response = urllib2.urlopen(str_url)
        root = etree.parse(response, etree.HTMLParser())
        different_difficulties = root.findall("//td[@class=\"title nowrap\"]/a")
        print_associations(root, url, monster)
        for durl in different_difficulties:
            request =  domain + 'en/' + durl.attrib["href"]
            response = urllib2.urlopen(request)
            root_in = etree.parse(response, etree.HTMLParser())
            print_associations(root_in, durl, monster)


def update_bank(root, url):
    parties = root.findall("//td[@class=\"pt\"]")
    grand_parties[url.text] = parties
    if parties:
        for party in parties:
            members = []
            for elem in party.iter():
                if 'href' in elem.attrib:
                    image = elem.find("img")
                    if (image != None):
                        title = image.attrib['title']
                        members.append(title)
            update_specific_monsters(url.text, members)

def update_specific_monsters(dungeon, members):
    placement = 0
    for member in members:
        idnum = int(non_decimal.sub('', member))
        if idnum not in mainbank.bank:
            mainbank.bank[idnum] = MonsterData(idnum)
        monster = mainbank.bank[idnum]
        monster.update_party_data(dungeon, members)
        monster.add_one_dungeon(dungeon)
        #check to see if leader/friend/sub?
        if placement == 0:
            monster.add_one_leader()
            monster.add_one()
        elif placement == len(members) - 1:
            monster.add_one_friend()
        else:
            monster.add_one_sub()
            monster.add_one()
        #iterate other members to see association
        others_placement = 0
        for omember in members:
            if placement != others_placement or placement != len(members) - 1:
                monster.add_one_teammate(omember)
        placement += 1

"""
Given a root html, the url and the monster number
we print out all parties associated with current dungeon
that has the monster in question. Also updates monster
information
"""
def print_associations(root, url, monster):
    dungeon_counter = 0
    parties = root.findall("//td[@class=\"pt\"]")
    grand_parties[url.text] = parties
    assoc_parties = get_assoc(monster.monster_num, parties)
    if assoc_parties:
        print '========================================='
        print url.text
        for party in assoc_parties:
            dungeon_counter += 1
            monster.add_one_dungeon(url.text)
            placement = 0 # to figure out placement
            for elem in party.iter():
                if 'href' in elem.attrib:
                    image = elem.find("img")
                    if (image != None):
                        title = image.attrib['title']
                        print title
                        idnum = int(non_decimal.sub('',title))
                        update_monster_info(placement, idnum, title, monster)
                        placement += 1
            print '======================'

"""
updates the monster info according to the placement of 
the monster in the team and other monsters that are
teamed up with this monster.
"""
def update_monster_info(placement, idnum, title, monster):
    if idnum == monster.monster_num:
        monster.add_one()
        if placement == 0:
            monster.add_one_leader()
        elif placement == 5:
            monster.add_one_friend()
        else:
            monster.add_one_sub()
    else:
        if placement != 5:
            monster.add_one_teammate(title)

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
def get_dungeon_urls():
    response = urllib2.urlopen(start_domain)
    root = etree.parse(response, etree.HTMLParser())
    dungeon_urls = root.findall("//td[@class=\"dungeonname\"]/a")
    return dungeon_urls

if __name__ == "__main__":
    main()
