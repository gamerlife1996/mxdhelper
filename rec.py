import cv2
import numpy
import mss
import pyautogui
import time
import json
import sys
import pytesseract
import os
import re

custom_config = r'-l chi_sim --psm 7'

class ShopHelper:
    
    def RecognizeText(self, crop):
        enlarge = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        threshold = cv2.threshold(enlarge, 128, 255, cv2.THRESH_BINARY)[1]
        text = pytesseract.image_to_string(threshold, config=custom_config)
        text = text.replace(' ','').replace('\n','').replace('','')
        # cv2.imshow("crop", crop)
        # cv2.imshow("thresh", threshold)
        # cv2.waitKey(0)
        return text


    def RecognizeTextEx(self, _left, _top, _width, name):
        crop = self.scr[_top:_top+20, _left:_left+_width]
        enlarge = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        threshold = cv2.threshold(enlarge, 210, 255, cv2.THRESH_BINARY_INV)[1]
        text = pytesseract.image_to_string(threshold, config=custom_config)
        text = text.replace(' ','').replace('\n','').replace('','')
        if len(text)>0:
            # cv2.imwrite(name+".jpg", threshold)
            print(text)
        return text


    def ReadGoods(self, good_list, start=0):
        crop = self.scr[goods_top+start*40:goods_bottom, goods_left:goods_left+goods_width]
        enlarge = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        threshold = cv2.threshold(enlarge, 128, 255, cv2.THRESH_BINARY)[1]
        text = pytesseract.image_to_string(threshold, config=r'-l chi_sim --psm 6')
        text = text.replace(' ','').replace('','')
        lines_raw = text.split('\n')
        lines = []
        for line in lines_raw:
            if len(line) > 0:
                lines.append(line)
        
        for index in range(0, int(len(lines)/2)):
            self.index = self.index + 1
            item_top = goods_top + (index + start) * 40
            available = self.IsAvailable(item_top)
            crop = self.scr[item_top:item_top+40, goods_left-38:goods_left+goods_width]
            cv2.imwrite(self.path + '/' + str(self.index)+".jpg", crop, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            
            self.CaptureItemDetail(item_top)

            json_good = {'index':self.index, 'name':lines[2*index], 'price':lines[2*index+1], 'available':available}
            good_list.append(json_good)


    def ClickShop(self, x, y):
        shop_title = self.RecognizeText(440, 142, 400, "title")

        json_shop = {}
        json_shop['title'] = shop_title
        good_list = []

        self.ReadGoods(good_list)
        if self.IsMatch(slider_top_img):
            count = self.ScrollToEnd()
            self.ReadGoods(good_list, 5-count)

        json_shop['goods'] = good_list
        return json_shop


    def GetShops(self, img):
        result = cv2.matchTemplate(self.scr, img, cv2.TM_CCOEFF_NORMED)

        w = img.shape[1]
        h = img.shape[0]

        threshold = .60
        yloc, xloc = numpy.where(result >= threshold)

        rectangles = []
        for (x, y) in zip(xloc, yloc):
            rectangles.append([int(x), int(y), int(w), int(h)])
            rectangles.append([int(x), int(y), int(w), int(h)])

        rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
        return rectangles


    def DoShops(self, img):
        rects = self.GetShops(img)
        for rect in rects:
            time_start = time.perf_counter()
            shop_json = self.ClickShop(window_rect[0]+rect[0]+30, window_rect[1]+rect[1]-20)
            time_end = time.perf_counter()
            print("time",time_end-time_start)
            if shop_json != None:
                self.json_map['shops'].append(shop_json)
            time.sleep(0.1)


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

                    json_good['price'] = self.RecognizeText(good[20:, 40:])
                    print(json_good['price'])

                    cv2.imwrite(good_path + '.jpg', good, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                    os.remove(good_path + '.png')

                    detail = cv2.imread(good_path + '_detail.png')
                    cv2.imwrite(good_path + '_detail.jpg', detail, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                    os.remove(good_path + '_detail.png')

        json_text = json.dumps(json_all_maps, indent=4, ensure_ascii=False, separators=(',', ': '))

        with open(self.path + '/data.json', mode='w', encoding='utf-8') as f:
            f.write(json_text)


        return


        dirs = os.listdir(self.path)
        for dir in dirs:
            if dir == 'data.json':
                continue
            print(dir)
            pics = os.listdir(self.path + '/' + dir)
            for pic in pics:
                if pic.endswith('_detail.png'):
                    continue
                elif pic.startswith('shop_'):
                    continue
                else:
                    good = cv2.imread(self.path + '/' + dir + '/' + pic)
                    name = self.RecognizeText(good[0:20, 40:])
                    price = self.RecognizeText(good[20:, 40:])
        return

        json_all_maps = {}
        if len(sys.argv) == 3 and sys.argv[2] == '-c':
            if os.path.exists('data.json'):
                os.remove('data.json')
            json_all_maps["maps"] = []
            json_all_maps["starttime"] = time.time()
        else:
            if not os.path.exists('data.json'):
                print("no json file, please add '-c' to create one!")
                return
            with open("data.json", mode='r', encoding='utf-8') as f:
                json_all_maps = json.loads(f.read())

        self.GrabScreen()

        self.json_map = {}
        self.json_map['map'] = self.path
        self.json_map['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        self.json_map['shops'] = []

        self.index = 0

        self.DoShops(shop_fairy_img)
        self.DoShops(shop_bear_img)
        self.DoShops(shop_maid_img)
        self.DoShops(shop_robot_img)

        json_all_maps["maps"].append(self.json_map)

        json_text = json.dumps(json_all_maps, indent=4, ensure_ascii=False, separators=(',', ': '))

        with open('data.json', mode='w', encoding='utf-8') as f:
            f.write(json_text)

        print("Done")


sh = ShopHelper()
time_start = time.perf_counter()
sh.CaptureAllShops()
time_end = time.perf_counter()
print("time",time_end-time_start)
