import urllib2
import fileinput
import re
import json
import operator
from collections import Counter
from lxml import etree

#this corresponds to the main site we are scraping data off of.
#change if this link ever breaks.
domain = 'http://www.puzzledragonx.com/'
#this corresponds to the large dungeon list in puzzledragonx
#change is this link ever breaks.
start_domain = 'http://www.puzzledragonx.com/?dir=1'
grand_parties = {}
associated_parties = {}
non_decimal = re.compile(r'[^\d]+')

class MonsterData:
    """
    The constructor of the monster data,
    takes in monster number.
    """
    def __init__(self, monster_num):
        self.monster_num = monster_num
        self.synergy = Counter()
        self.dungeons = Counter()
        self.dungeon_ratio = {}
        self.leader = 0
        self.friend = 0
        self.sub = 0
        self.appearance = 0

    def add_one_leader(self):
        self.leader += 1

    def add_one_friend(self):
        self.friend += 1

    def add_one_sub(self):
        self.sub += 1

    def add_one(self):
        self.appearance += 1

    def add_one_teammate(self, monster_id):
        self.synergy[monster_id] += 1

    def add_one_dungeon(self, dungeon):
        self.dungeons[dungeon] += 1

    def get_topx_teammate(self, x):
        return self.synergy.most_common(x)

    def get_topx_dungeons(self, x):
        return self.dungeons.most_common(x)

    def __str__(self):
        best_dungeon = max(self.dungeon_ratio.iteritems(), key=operator.itemgetter(1))[0]
        return str('monster id:' + str(self.monster_num) + '\n' +
                   'top ten monster friends: ' + str(self.synergy.most_common(10)) + '\n' + 
                   'top ten dungeons: ' + str(self.dungeons.most_common(10)) + '\n' +
                   'best dungeon ratio: ' + str(best_dungeon) + \
                   ' with ratio:' + str(self.dungeon_ratio[best_dungeon]) + '\n' + 
                   'leader:' + str(self.leader) + '\n' + 
                   'friend:' + str(self.friend) + '\n' +
                   'sub:' + str(self.sub) + '\n' +
                   'appearances:' + str(self.appearance) + '\n')

class PartyData:
    def __init__(self, party_list, dungeon, stone):
        self.stone = stone
        self.dungeon = dungeon
        self.leader = party_list[0]
        self.subs = party_list[1:len(party_list) - 1]
        self.friend = party_list[len(party_list)]


class MonsterDataEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, MonsterData):
            return {obj.monster_num:{'synergy':obj.synergy, 'dungeons':obj.dungeons, 'dungeon_ratios':obj.dungeon_ratio, \
                    'leader':obj.leader, 'friend':obj.friend, 'sub':obj.sub, 'appearance':obj.appearance}}
        return json.JSONEncoder.default(self, obj)

def main():
    dungeon_urls = get_dungeon_urls()
    print 'please enter a monster number'
    for line in fileinput.input():
        line = non_decimal.sub('', line)
        monster_num = int(line)
        monster = MonsterData(monster_num)
        find_associations(dungeon_urls, monster)
        serialize(monster)
"""
Serialize monsters in to a json file.
"""
def serialize(monster):
    data = json.dumps(monster, cls=MonsterDataEncoder)
    with open(str(monster.monster_num) + '.json', 'w') as outfile:
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
        monster.dungeon_ratio[url.text] = float(float(dungeon_counter) / float(len(parties)))

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
