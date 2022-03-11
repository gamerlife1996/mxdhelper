import cv2
import time
import json
import sys
import os
from tesserocr import PyTessBaseAPI, RIL, iterate_level, PSM
from PIL import Image
import shutil
import numpy

api = PyTessBaseAPI(lang='chi_sim', psm=PSM.SINGLE_LINE)

prefix = cv2.imread('prefix.png', 0)
suffix = cv2.imread('suffix.png', 0)
comma = cv2.imread('comma.png', 0)

class ShopHelper:

    def RecognizeText(self, crop):
        enlarge = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        threshold = cv2.threshold(enlarge, 128, 255, cv2.THRESH_BINARY)[1]
        api.SetImage(Image.fromarray(threshold))
        text = api.GetUTF8Text()
        text = text.replace(' ','').replace('\n','').replace('','')
        return text


    def RecognizeAllShop(self):

        with open('data.json', mode='r', encoding='utf-8') as f:
            json_all_maps = json.loads(f.read())

        number_img = []
        for i in range(0, 10):
            number_img.append(cv2.imread(str(i)+'.png', 0))

        for json_map in json_all_maps['maps']:
            print(json_map['map'])
            for json_shop in json_map['shops']:

                for json_good in json_shop['goods']:
                    good_path = json_map['map'] + '/' + str(json_good['index'])
                    good = cv2.imread(good_path + '.png')

                    crop = good[20:38, 40:]
                    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                    thres = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)[1]

                    result = cv2.matchTemplate(thres, prefix, cv2.TM_CCOEFF_NORMED)
                    _, prefix_val, _, prefix_loc = cv2.minMaxLoc(result)

                    result = cv2.matchTemplate(thres, suffix, cv2.TM_CCOEFF_NORMED)
                    _, suffix_val, _, suffix_loc = cv2.minMaxLoc(result)

                    if prefix_val > 0.9:
                        start = prefix_loc[0]+len(prefix[0])+2
                        number = thres[suffix_loc[1]+2:suffix_loc[1]+11, start:suffix_loc[0]]
                    else:
                        number = thres[suffix_loc[1]+2:suffix_loc[1]+11, 4:suffix_loc[0]]

                    price = ''
                    number_count = len(number[0]) // 6
                    for i in range(0, number_count):
                        single_num = number[:, i*6:i*6+5]
                        if numpy.array_equiv(single_num, comma):
                            price += ','
                        else:
                            for j in range(0, 10):
                                if numpy.array_equiv(single_num, number_img[j]):
                                    price += str(j)

                    print(price)

                    cv2.imshow("thres",thres)
                    cv2.imshow("number",number)
                    cv2.waitKey(0)



        print("Done")
        return



sh = ShopHelper()

time_start = time.perf_counter()
sh.RecognizeAllShop()
time_end = time.perf_counter()

print("time",time_end-time_start)

api.End()