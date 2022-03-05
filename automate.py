from key import SetFocus, PressKey, ReleaseKey
import time
import win32gui
import capture
import sys
import cv2
import numpy
import mss

import win32gui
import win32api

window_handle = win32gui.FindWindow("MapleStoryClass", None)
window_rect   = win32gui.GetWindowRect(window_handle)

sct = mss.mss()

hwnd = win32gui.FindWindow("MapleStoryClass", None)

hero_img = cv2.imread('source/hero.png')

sh = capture.ShopHelper()

class keycode:
    c = 0x2E
    alt = 0x38
    up = 0x48
    left = 0x4B
    right = 0x4D
    down = 0x50

def DoKey(code, t=0.05):
    PressKey(code)
    time.sleep(t)
    ReleaseKey(code)

def JumpFar(wait=0.6):
    DoKey(keycode.alt,0.01)
    time.sleep(0.02)
    DoKey(keycode.c,0.01)
    time.sleep(wait) # wait til landing

def DoMapFirstFloor(path):
    # enter map
    DoKey(keycode.up)
    time.sleep(3)

    shopCount = sh.GetFairyShopCount()
    if shopCount > 5:
        # jump left
        DoKey(keycode.left)
        time.sleep(0.1)
        JumpFar(0.5)
        JumpFar(0.2)
        PressKey(keycode.up)
        time.sleep(1.5)
        ReleaseKey(keycode.up)
        time.sleep(2)

    # capture
    sh.Start(path)
    time.sleep(0.1)
    
    if shopCount > 5:
        PressKey(keycode.right)
        time.sleep(0.1)
        JumpFar()
        time.sleep(0.4)
        ReleaseKey(keycode.right)

        # jump down
        PressKey(keycode.down)
        time.sleep(0.1)
        DoKey(keycode.alt)
        time.sleep(0.1)
        ReleaseKey(keycode.down)
        time.sleep(0.5)
        # DoKey(keycode.right, 0.8)
    
    # exit map
    DoKey(keycode.up)
    time.sleep(4)


def DoMapSecondFloor(path):
    # enter map
    DoKey(keycode.up)
    time.sleep(3)

    shopCount = sh.GetFairyShopCount()
    if shopCount > 5:
        # jump right
        JumpFar(0.2)
        PressKey(keycode.up)
        time.sleep(1.5)
        ReleaseKey(keycode.up)
        time.sleep(2)

    # capture
    sh.Start(path)
    time.sleep(0.1)

    if shopCount > 5:
        # jump left
        PressKey(keycode.left)
        time.sleep(0.1)
        DoKey(keycode.alt)
        time.sleep(1.3)
        ReleaseKey(keycode.left)

    # exit map
    DoKey(keycode.up)
    time.sleep(4)


def DoMapThirdFloor(path):
    # enter map
    DoKey(keycode.up)
    time.sleep(3)

    shopCount = sh.GetFairyShopCount()
    if shopCount > 5:
        # jump right
        JumpFar()
        JumpFar()
        JumpFar()
        JumpFar(0.2)
        PressKey(keycode.up)
        time.sleep(1.8)
        ReleaseKey(keycode.up)
        time.sleep(2)

    # capture
    sh.Start(path)
    time.sleep(0.1)

    if shopCount > 5:
        # jump left
        DoKey(keycode.left)
        time.sleep(0.1)
        JumpFar()
        JumpFar()
        JumpFar()
        DoKey(keycode.left, 0.8)

        time.sleep(1)
        sh.Click(30, 430)
        time.sleep(0.1)
        if (sh.IsInShop()):
            sh.Start(path)

    # exit map
    DoKey(keycode.up)
    time.sleep(4)


def KeyPress(channel):
    SetFocus(hwnd)

    if str(channel) == "1":
        FirstFloor(channel)
        FirstToSecond()
        SecondFloor(channel)
        SecondToThird()
        ThirdFloor(channel)
    else:
        FirstFloor(channel)


class Automator:

    def WalkTo(self, targetX):
        xdiff = self.hero_x - targetX
        # print(self.hero_x, targetX, xdiff)
        if xdiff == 0:
            # success only if two consective good
            if self.goodCount == 10:
                return True
            else:
                self.goodCount = self.goodCount + 1
        else:
            self.goodCount = 0
            if xdiff < -70:
                ReleaseKey(keycode.left)
                PressKey(keycode.right)
            elif xdiff > 70:
                ReleaseKey(keycode.right)
                PressKey(keycode.left)
            else:
                ReleaseKey(keycode.left)
                ReleaseKey(keycode.right)
                if xdiff < 0:
                    DoKey(keycode.right, 0.1)
                elif xdiff > 0:
                    DoKey(keycode.left, 0.1)

    def Walk(self, target):
        rect = {"left":window_rect[0]+5, "top":window_rect[1]+95, "width":200, "height":100}
        while True:
            scr = numpy.array(sct.grab(rect))
            scr = scr[:,:,:3]

            result = cv2.matchTemplate(scr, hero_img, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            self.hero_x = max_loc[0]

            if self.WalkTo(target):
                print("arrive")
                break

    def Test(self, channel):
        
        SetFocus(hwnd)

        firstFloor = { 1:116, 2:125, 3:135, 4:147, 5:158, 6:168, "height":64, "up":109 }
        secondFloor = { 13:122, 14:132, 15:142, 16:153, 17:163, "height":30, "up":115 }
        thirdFloor = { 18:124, 19:133, 20:142, 21:152, 22:161, "height":13 }

        for i in range(1,7):
            self.Walk(firstFloor[i])
            DoMapFirstFloor(str(channel)+'-'+str(i))

        
        if str(channel) == "1":
            self.Walk(firstFloor['up'])
            DoKey(keycode.up)
            time.sleep(1)
            DoKey(keycode.up)

            for i in range(13,18):
                self.Walk(secondFloor[i])
                DoMapSecondFloor(str(channel)+'-'+str(i))

            self.Walk(secondFloor['up'])
            DoKey(keycode.up)

            for i in range(18,23):
                self.Walk(thirdFloor[i])
                DoMapThirdFloor(str(channel)+'-'+str(i))
            
        

auto = Automator()
auto.Test(sys.argv[1])