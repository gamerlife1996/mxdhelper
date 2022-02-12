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

import win32gui

window_handle = win32gui.FindWindow("MapleStoryClass", None)
window_rect   = win32gui.GetWindowRect(window_handle)

sct = mss.mss()

shop_fairy_img = cv2.imread('source/shop.png')
shop_bear_img = cv2.imread('source/bear.png')
shop_maid_img = cv2.imread('source/maid.png')
shop_robot_img = cv2.imread('source/robot.png')

inshop_img = cv2.imread('source/inshop.png')
slider_top_img = cv2.imread('source/top.png')
slider_bottom_img = cv2.imread('source/bottom.png')

organizing_img = cv2.imread('source/organizing.png')

self_shop_img = cv2.imread('source/self.png')

goods_top = 288
goods_bottom = 488
goods_left = 465
goods_width = 160

custom_config = r'-l chi_sim --psm 7'

class ShopHelper:
    
    def GrabScreen(self, rect = window_rect):
        self.scr = numpy.array(sct.grab(rect))
        self.scr = self.scr[:,:,:3]


    def RecognizeText(self, _left, _top, _width, name):
        crop = self.scr[_top:_top+20, _left:_left+_width]
        enlarge = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        threshold = cv2.threshold(enlarge, 128, 255, cv2.THRESH_BINARY)[1]
        text = pytesseract.image_to_string(threshold, config=custom_config)
        text = text.replace(' ','').replace('\n','').replace('','')
        # if len(text)>0:
        #     # cv2.imwrite(name+".jpg", threshold)
        #     print(text)
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


    def IsAvailable(self, _top):
        crop = self.scr[_top:_top+40, goods_left:goods_left+goods_width]
        color = crop[10, 150]
        return bool(color[0] <= 221)

    def CaptureItemDetail(self, item_top):
        mouse_pos = (window_rect[0]+goods_left-35, window_rect[1]+item_top+6)
        pyautogui.moveTo(mouse_pos[0], mouse_pos[1], 0.1)
        detail_scr = numpy.array(sct.grab({"top": window_rect[1]+goods_top, "left": mouse_pos[0], "width": 300, "height": 500}))
        detail_scr = detail_scr[:,:,:3]
        
        scr_gray = cv2.cvtColor(detail_scr, cv2.COLOR_BGR2GRAY)
        _, scr_thresh = cv2.threshold(scr_gray, 60, 255, cv2.THRESH_BINARY_INV)

        detail_bg = self.scr[goods_top:goods_top+500, goods_left-35:goods_left-35+300 ]
        front_mask = detail_scr - detail_bg
        img_gray = cv2.cvtColor(front_mask, cv2.COLOR_BGR2GRAY)
        _, front_thresh = cv2.threshold(img_gray, 10, 255, cv2.THRESH_BINARY)
        
        # multiply mask
        mul_thresh = cv2.multiply(scr_thresh, front_thresh)

        # find tip area
        contours, hierarchy = cv2.findContours(mul_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        x,y,w,h = cv2.boundingRect(max(contours, key = cv2.contourArea))
        detail_scr = detail_scr[y:y+h, x:x+w]

        # remove bg
        lower_black = numpy.array([0,0,0], dtype = "uint16")
        upper_black = numpy.array([70,70,70], dtype = "uint16")
        black_mask = ~cv2.inRange(detail_scr, lower_black, upper_black)
        detail_scr = cv2.bitwise_and(detail_scr, detail_scr, mask=black_mask)

        cv2.imwrite(self.path + '/' + str(self.index)+"_detail.jpg", detail_scr, [int(cv2.IMWRITE_JPEG_QUALITY), 75])

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


    def ScrollToEnd(self):
        count = 0
        pyautogui.moveTo(window_rect[0]+637, window_rect[1]+478)
        for i in range(0,5):
            pyautogui.scroll(-120)
            count = count + 1
            self.GrabScreen()
            if self.IsMatch(slider_bottom_img):
                break
        return count


    def IsMatch(self, img):
        result = cv2.matchTemplate(self.scr, img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        return max_val > 0.9


    def ClickShop(self, x, y):
        pyautogui.moveTo(x, y)
        pyautogui.doubleClick()

        # wait for shop to open
        while True:
            self.GrabScreen()
            if self.IsMatch(inshop_img):
                break
            if self.IsMatch(self_shop_img):
                pyautogui.click(window_rect[0]+784, window_rect[1]+448)
                return
            if self.IsMatch(organizing_img):
                pyautogui.click(window_rect[0]+787, window_rect[1]+450)
                return

        pyautogui.click(window_rect[0]+100, window_rect[1]+100)
        self.GrabScreen()

        shop_title = self.RecognizeText(440, 142, 400, "title")

        json_shop = {}
        json_shop['title'] = shop_title
        good_list = []

        self.ReadGoods(good_list)
        if self.IsMatch(slider_top_img):
            count = self.ScrollToEnd()
            self.ReadGoods(good_list, 5-count)

        json_shop['goods'] = good_list

        # close shop
        pyautogui.click(window_rect[0]+603, window_rect[1]+256)
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
            print('folder name is empty, default is test.')
            self.path = 'test'
        else:
            self.path = sys.argv[1]

        if not os.path.exists(self.path):
            os.makedirs(self.path)

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
