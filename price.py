
import json
import sys
import os
import shutil

# load corrected names data
text_correct = {}
with open('original.txt', mode='r', encoding='utf-8') as f:
    origin_array = f.read().split('\n')
with open('correction.txt', mode='r', encoding='utf-8') as f:
    correct_array = f.read().split('\n')
for i in range(len(origin_array)):
    text_correct[origin_array[i]] = correct_array[i]

lowest_avail_price = {}
all_names = []

for folder in os.listdir('old_data'):
    with open('old_data/' + folder + '/data.json', mode='r', encoding='utf-8') as f:
        data = json.loads(f.read())
        time = data['starttime']
        name2price = {}
        for _map in data['maps']:
            for shop in _map['shops']:
                for good in shop['goods']:
                    name = good['name']
                    if name in text_correct:
                        name = text_correct[name]

                    if len(good['price']) == 0: # skip invalid price
                        continue

                    # if not good['available']: # skip unavail good
                    #     continue

                    price = int(good['price'].replace(',',''))

                    if name not in all_names:
                        all_names.append(name)
                    
                    if name not in name2price:
                        name2price[name] = price
                    else:
                        if price < name2price[name]:
                            name2price[name] = price

        lowest_avail_price[time] = name2price

json_all = []

for name in all_names:
    print(name)
    o = {}
    o['name'] = name

    l = []
    for time, d in lowest_avail_price.items():
        if name in d:
            l.append({'time':time, 'price':d[name]})
    
    o['prices'] = l

    json_all.append(o)


json_text = json.dumps(json_all, indent=4, ensure_ascii=False, separators=(',', ': '))

with open('price.json', mode='w', encoding='utf-8') as f:
    f.write(json_text)

# copy json file
shutil.copy('price.json', 'E:\gamerlife1996.github.io\src\\views\price.json')