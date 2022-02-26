import cv2
import time
import json
import sys
import os
from tesserocr import PyTessBaseAPI, RIL, iterate_level, PSM
from PIL import Image
import shutil

api = PyTessBaseAPI(lang='chi_sim', psm=PSM.SINGLE_LINE)

class ShopHelper:

    def MoveFiles(self):
        with open('data.json', mode='r', encoding='utf-8') as f:
            json_all_maps = json.loads(f.read())

        dest = str(json_all_maps['starttime'])
        os.makedirs(dest)

        for json_map in json_all_maps['maps']:
            shutil.move(json_map['map'], dest)

        shutil.move('data.json', dest)
        self.path = dest


    def MoveFilesAfterFinish(self):
        # delete old data
        dirs = os.listdir('E:\gamerlife1996.github.io\public')
        for dir in dirs:
            dirpath = 'E:\gamerlife1996.github.io\public\\' + dir
            if os.path.isdir(dirpath):
                shutil.rmtree(dirpath)

        # copy new data
        shutil.copytree(self.path, 'E:\gamerlife1996.github.io\public\\'+self.path)

        # move data to old_data folder
        shutil.move(self.path, 'old_data')

        # move json file
        shutil.move('E:\gamerlife1996.github.io\public\\'+self.path+'\data.json', 'E:\gamerlife1996.github.io\src\\views\data.json')

        # starts building
        os.chdir('E:\gamerlife1996.github.io\\')
        os.system('build.bat')
    

    def RecognizeText(self, crop):
        enlarge = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        threshold = cv2.threshold(enlarge, 128, 255, cv2.THRESH_BINARY)[1]
        api.SetImage(Image.fromarray(threshold))
        text = api.GetUTF8Text()
        text = text.replace(' ','').replace('\n','').replace('','')
        return text


    def RecognizeAllShop(self):

        # load corrected names data
        text_correct = {}
        with open('original.txt', mode='r', encoding='utf-8') as f:
            origin_array = f.read().split('\n')
        with open('correction.txt', mode='r', encoding='utf-8') as f:
            correct_array = f.read().split('\n')
        for i in range(len(origin_array)):
            text_correct[origin_array[i]] = correct_array[i]

        not_corrected_names = []

        with open(self.path + '/data.json', mode='r', encoding='utf-8') as f:
            json_all_maps = json.loads(f.read())

        for json_map in json_all_maps['maps']:
            print(json_map['map'])
            for json_shop in json_map['shops']:
                shop = cv2.imread(self.path + '/' + json_map['map'] + '/shop_' + str(json_shop['index']) + '.png')
                json_shop['title'] = self.RecognizeText(shop)
                print(json_shop['title'])
                os.remove(self.path + '/' + json_map['map'] + '/shop_' + str(json_shop['index']) + '.png')

                for json_good in json_shop['goods']:
                    good_path = self.path + '/' + json_map['map'] + '/' + str(json_good['index'])
                    good = cv2.imread(good_path + '.png')

                    # get corrected name
                    origin_name = self.RecognizeText(good[0:20, 40:])
                    if origin_name in text_correct:
                        json_good['name'] = text_correct[origin_name]
                    else:
                        json_good['name'] = origin_name
                        if origin_name not in not_corrected_names:
                            not_corrected_names.append(origin_name)

                    cv2.imwrite(good_path + '.jpg', good, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                    os.remove(good_path + '.png')

        json_text = json.dumps(json_all_maps, indent=4, ensure_ascii=False, separators=(',', ': '))

        with open(self.path + '/data.json', mode='w', encoding='utf-8') as f:
            f.write(json_text)

        with open('not_corrected.txt', mode='w', encoding='utf-8') as f:
            f.write('\n'.join(not_corrected_names))
        print("found " + str(len(not_corrected_names)) +" not corrected names. saved to not_corrected.txt")
        for name in not_corrected_names:
            print(name)

        print("Done")
        return



sh = ShopHelper()
sh.MoveFiles()

time_start = time.perf_counter()
sh.RecognizeAllShop()
time_end = time.perf_counter()

print("time",time_end-time_start)

api.End()

sh.MoveFilesAfterFinish()