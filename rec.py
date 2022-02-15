import cv2
import time
import json
import sys
import pytesseract
import os
from tesserocr import PyTessBaseAPI, RIL, iterate_level, PSM
from PIL import Image

api = PyTessBaseAPI(lang='chi_sim', psm=PSM.SINGLE_LINE)

class ShopHelper:
    
    def RecognizeText(self, crop):
        enlarge = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        threshold = cv2.threshold(enlarge, 128, 255, cv2.THRESH_BINARY)[1]
        api.SetImage(Image.fromarray(threshold))
        text = api.GetUTF8Text()
        text = text.replace(' ','').replace('\n','').replace('','')
        return text


    def CaptureAllShops(self):
        if len(sys.argv) < 2:
            print('please enter folder name.')
            return
        else:
            self.path = sys.argv[1]

        if not os.path.exists(self.path):
            print('folder' + self.path + ' not exist.')
            return

        
        if not os.path.exists(self.path + '/data.json'):
            print("no json file.")
            return
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

                    json_good['name'] = self.RecognizeText(good[0:20, 40:])
                    print(json_good['name'])

                    # json_good['price'] = self.RecognizeText(good[20:, 40:])
                    # print(json_good['price'])

                    cv2.imwrite(good_path + '.jpg', good, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                    os.remove(good_path + '.png')

        json_text = json.dumps(json_all_maps, indent=4, ensure_ascii=False, separators=(',', ': '))

        with open(self.path + '/data.json', mode='w', encoding='utf-8') as f:
            f.write(json_text)


        print("Done")
        return


sh = ShopHelper()

time_start = time.perf_counter()
sh.CaptureAllShops()
time_end = time.perf_counter()

print("time",time_end-time_start)

api.End()