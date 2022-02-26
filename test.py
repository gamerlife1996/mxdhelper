import tesserocr
from PIL import Image
import time
import cv2
import numpy
from tesserocr import PyTessBaseAPI, RIL, iterate_level, PSM
import sys
import json

api = PyTessBaseAPI(lang='chi_sim', psm=PSM.SINGLE_LINE)
# print(api.GetUTF8Text())
# print(api.AllWordConfidences())

class ShopHelper:

    def RecognizeText(self, crop):
        enlarge = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        threshold = cv2.threshold(enlarge, 128, 255, cv2.THRESH_BINARY)[1]
        
        img = Image.fromarray(threshold)
        api.SetImage(img)
        text = api.GetUTF8Text()
        text = text.replace(' ','').replace('\n','').replace('','')
        return text

    def CaptureAllShops(self):
    
        all_names = []

        with open('data.json', mode='r', encoding='utf-8') as f:
            json_all_maps = json.loads(f.read())

        for json_map in json_all_maps['maps']:
            # print(json_map['map'])

            for json_shop in json_map['shops']:
                for json_good in json_shop['goods']:
                    # print(json_good['name'])
                    if json_good['name'] not in all_names:
                        all_names.append(json_good['name'])

        # all_name_text = '\n'.join(all_names)
        # with open('correction.txt', mode='w', encoding='utf-8') as f:
        #     f.write(all_name_text)
        # print(len(all_name_text))


sh = ShopHelper()

time_start = time.perf_counter()

sh.CaptureAllShops()

time_end = time.perf_counter()
print("time",time_end-time_start)


api.End()