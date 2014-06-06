import json
from collections import Counter

class MonsterBank:
    def __init__(self):
        self.bank = {}

class MonsterBankEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, MonsterBank):
            serializable = {}
            for key, value in obj.bank.items():
                serializable[key] = value.get_jsonable()
            return serializable
        return json.JSONEncoder.default(self, obj)


class MonsterData:
    """
    The constructor of the monster data,
    takes in monster number.
    """
    def __init__(self, monster_num):
        self.monster_num = monster_num
        self.synergy = Counter()
        self.dungeons = Counter()
        self.partydata = {}
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

    def update_party_data(self, dungeon, party):
        if dungeon not in self.partydata:
            self.partydata[dungeon] = [party,]
        else:
            self.partydata[dungeon].append(party)

    def __str__(self):
        return str('monster id:' + str(self.monster_num) + '\n' +
                   'top ten monster friends: ' + str(self.synergy.most_common(10)) + '\n' + 
                   'top ten dungeons: ' + str(self.dungeons.most_common(10)) + '\n' +
                   'leader:' + str(self.leader) + '\n' + 
                   'friend:' + str(self.friend) + '\n' +
                   'sub:' + str(self.sub) + '\n' +
                   'appearances:' + str(self.appearance) + '\n')

    def get_jsonable(self):
        return {'id':self.monster_num, 'synergy':self.synergy, 'dungeons':self.dungeons, \
                'leader':self.leader, 'friend':self.friend, \
                'sub':self.sub, 'appearance':self.appearance, 'dungeon_parties':self.partydata}

class MonsterDataEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, MonsterData):
            return {obj.monster_num:{'synergy':obj.synergy, 'dungeons':obj.dungeons, \
                    'leader':obj.leader, 'friend':obj.friend, \
                    'sub':obj.sub, 'appearance':obj.appearance, 'dungeon_parties':obj.partydata}}
        return json.JSONEncoder.default(self, obj)














