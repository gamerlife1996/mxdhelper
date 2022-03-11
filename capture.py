import cv2
import numpy
import mss
import pyautogui
import time
import json
import sys
import os
import re
import random

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
sort_img = cv2.imread('source/sort.png')

self_shop_img = cv2.imread('source/self.png')

goods_top = 288
goods_bottom = 488
goods_left = 465
goods_width = 160

class ShopHelper:
    
    
    def Grab(self, rect=window_rect):
        return numpy.array(sct.grab(rect))


    def GrabScreen(self, rect = window_rect):
        self.scr = numpy.array(sct.grab(rect))
        self.scr = self.scr[:,:,:3]

    def IsAvailable(self, _top):
        crop = self.scr[_top:_top+40, goods_left:goods_left+goods_width]
        color = crop[10, 150]
        return bool(color[0] <= 221)

    def CaptureItemDetail(self, item_top):
        mouse_pos = (window_rect[0]+goods_left-35, window_rect[1]+item_top+6)
        pyautogui.moveTo(mouse_pos[0], mouse_pos[1], 0.1)
        time.sleep(0.01)
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
        return w,h


    def SaveGoods(self, good_list, start=0):
        for index in range(0, 5-start):
            self.index = self.index + 1
            item_top = goods_top + (index + start) * 40
            available = self.IsAvailable(item_top)
            crop = self.scr[item_top:item_top+40, goods_left-38:goods_left+goods_width]
            
            icon = crop[:,:38]
            mean = cv2.mean(icon)
            if mean[0] > 213.9 and mean[0] < 216 and mean[1] > 221 and mean[1] < 224 and mean[2] > 222 and mean[2] < 225:
                # empty
                return

            cv2.imwrite(self.path + '/' + str(self.index)+".png", crop)

            # 0.11s
            detailWidth, detailHeight = self.CaptureItemDetail(item_top)

            json_good = {'index':self.index, 'available':available, 'detailWidth':detailWidth, 'detailHeight':detailHeight}
            good_list.append(json_good)


    def IsMatch(self, img):
        result = cv2.matchTemplate(self.scr, img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        return max_val > 0.9


    def ScrollToEnd(self):
        count = 0
        pyautogui.moveTo(window_rect[0]+637, window_rect[1]+478)
        scroll_rect = {"left":window_rect[0]+620, "top":window_rect[1]+270, "width":50, "height":230}
        for i in range(0,5):
            pyautogui.scroll(-120)
            count = count + 1
            self.GrabScreen(scroll_rect)
            if self.IsMatch(slider_bottom_img):
                break
        return count

    def Click(self, x, y):
        pyautogui.moveTo(window_rect[0]+x, window_rect[1]+y)
        pyautogui.doubleClick()

    def IsInShop(self):
        self.GrabScreen()
        return self.IsMatch(inshop_img)

    def GetFairyShopCount(self):
        self.GrabScreen()
        rects = self.GetShops(shop_fairy_img)
        return len(rects)

    def ClickShop(self, x, y):
        pyautogui.moveTo(x, y)
        pyautogui.doubleClick()

        start_time = time.time()
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
            if self.IsMatch(organizing_img):
                pyautogui.click(window_rect[0]+780, window_rect[1]+460)
                return
            if time.time() - start_time > 1:
                print("waited too long, reclick shop")
                x_offset = random.randrange(-20, 20)
                y_offset = random.randrange(-20, 20)
                pyautogui.moveTo(x + x_offset, y + y_offset)
                pyautogui.doubleClick()

        pyautogui.click(window_rect[0]+100, window_rect[1]+100)

        self.GrabScreen()

        shop_title = self.scr[140:140+20, 440:440+400]

        good_list = []

        self.SaveGoods(good_list)
        if self.IsMatch(slider_top_img):
            count = self.ScrollToEnd()
            self.GrabScreen()
            self.SaveGoods(good_list, 5-count)

        if len(good_list) == 0:
            pyautogui.click(window_rect[0]+603, window_rect[1]+256)
            return

        # shop title
        cv2.imwrite(self.path + '/shop_' + str(self.shopIndex)+".png", shop_title)

        json_shop = {}
        json_shop['index'] = self.shopIndex

        self.shopIndex = self.shopIndex + 1

        json_shop['goods'] = good_list

        # close shop
        pyautogui.click(window_rect[0]+603, window_rect[1]+256)
        return json_shop


    def GetShops(self, img):
        result = cv2.matchTemplate(self.scr, img, cv2.TM_CCOEFF_NORMED)

        w = img.shape[1]
        h = img.shape[0]

        threshold = .80
        yloc, xloc = numpy.where(result >= threshold)

        rectangles = []
        for (x, y) in zip(xloc, yloc):
            rectangles.append([int(x), int(y), int(w), int(h)])
            rectangles.append([int(x), int(y), int(w), int(h)])

        rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
        return rectangles


    def DoShops(self, img, name):
        rects = self.GetShops(img)
        print('found ' + str(len(rects)) + ' ' + name + ' shops.')
        for rect in rects:
            time_start = time.perf_counter()
            shop_json = self.ClickShop(window_rect[0]+rect[0]+30, window_rect[1]+rect[1]-30)
            time_end = time.perf_counter()
            print("time",time_end-time_start)
            if shop_json != None:
                self.json_map['shops'].append(shop_json)
            time.sleep(0.1)


    def CaptureAllShops(self):
        self.GrabScreen()

        self.json_map = {}
        self.json_map['map'] = self.path
        self.json_map['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        self.json_map['shops'] = []

        self.index = 0
        self.shopIndex = 0

        self.DoShops(shop_fairy_img, 'fairy')
        self.DoShops(shop_bear_img, 'bear')
        self.DoShops(shop_maid_img, 'maid')
        self.DoShops(shop_robot_img, 'robot')

        self.json_all_maps["maps"].append(self.json_map)
        

    def AppendShop(self):
        lastShopInMap = self.this_json_map['shops'][-1]

        self.shopIndex = lastShopInMap['index'] + 1
        self.index = lastShopInMap['goods'][-1]['index']

        self.GrabScreen()

        shop_title = self.scr[140:140+20, 440:440+400]

        good_list = []

        self.SaveGoods(good_list)
        if self.IsMatch(slider_top_img):
            count = self.ScrollToEnd()
            self.GrabScreen()
            self.SaveGoods(good_list, 5-count)

        # shop title
        cv2.imwrite(self.path + '/shop_' + str(self.shopIndex)+".png", shop_title)

        json_shop = {}
        json_shop['index'] = self.shopIndex
        json_shop['goods'] = good_list

        self.this_json_map['shops'].append(json_shop)

        # close shop
        pyautogui.click(window_rect[0]+603, window_rect[1]+256)


    def Start(self, path):
        print("path="+path)
        self.path = path

        if self.GetFairyShopCount() == 0:
            print("no shop")
            return

        if not os.path.exists(path):
            os.makedirs(path)

        self.json_all_maps = {}
        if not os.path.exists('data.json'):
            self.json_all_maps["maps"] = []
            self.json_all_maps["starttime"] = int(time.time())
        else:
            with open("data.json", mode='r', encoding='utf-8') as f:
                self.json_all_maps = json.loads(f.read())

        isExist = False
        for json_map in self.json_all_maps['maps']:
            if json_map['map'] == path:
                self.this_json_map = json_map
                isExist = True
                print('found map')

        time_start = time.perf_counter()

        if isExist:
            self.AppendShop()
        else:
            self.CaptureAllShops()

        time_end = time.perf_counter()
        print("time",time_end-time_start)

        json_text = json.dumps(self.json_all_maps, indent=4, ensure_ascii=False, separators=(',', ': '))

        with open('data.json', mode='w', encoding='utf-8') as f:
            f.write(json_text)

        print("Done")