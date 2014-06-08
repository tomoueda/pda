from pdaclasses import *
import json
import ast

data = open('monster_data/694.json').read()
siren = json.loads(data)
print type(siren)
siren = ast.literal_eval(siren)
monster = customMonsterDataDecoder(siren)
print monster