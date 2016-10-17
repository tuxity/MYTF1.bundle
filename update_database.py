#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

keys_2_dump = ['programs', 'links']

database = requests.get('http://api.mytf1.tf1.fr/mobile/init?device=ios-smartphone').json()

for key in database.keys():
    if key in keys_2_dump:
        print('Dumping %s...' % key)
        with open('Contents/Resources/database/%s.json' % key , 'w') as outfile:
            json.dump(database['programs'], outfile)

print('done.')
