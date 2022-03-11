import key
from key import keycode
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


rect_firstFloor = {"left":window_rect[0]+24, "top":window_rect[1]+98, "width":88, "height":64}
rect_entry = {"left":window_rect[0]+5, "top":window_rect[1]+95, "width":200, "height":100}

firstFloor = { 1:116, 2:125, 3:135, 4:147, 5:158, 6:168, "height":64, "up":109 }
secondFloor = { 13:122, 14:132, 15:142, 16:153, 17:163, "height":30, "up":115 }
thirdFloor = { 18:124, 19:133, 20:142, 21:152, 22:161, "height":13 }

class Automator:

    def WaitForResponse(self, threshold=10):
        scr = sh.Grab()
        hasLoad = False
        activeFrameCount = 0
        while True:
            new_scr = sh.Grab()

            gray = cv2.cvtColor(new_scr, cv2.COLOR_BGR2GRAY)
            mean = cv2.mean(gray)[0]

            if mean < 80:
                if not hasLoad:
                    hasLoad = True
            else:
                if hasLoad:
                    diff = new_scr - scr
                    scr = new_scr
                    isFreeze = numpy.max(diff) == 0
                    if not isFreeze:
                        activeFrameCount += 1
                    else:
                        # freeze, reset count
                        activeFrameCount = 0

            if activeFrameCount > threshold:
                break

        time.sleep(0.1) # small buffer time
        print("finish loading")


    def DoMapFirstFloor(self, path):
        # enter map
        key.DoKey(keycode.up)
        self.WaitForResponse()
        
        shopCount = sh.GetFairyShopCount()
        if shopCount > 5:
            # jump left
            key.DoKey(keycode.left)
            time.sleep(0.1)
            key.JumpFar(0.5)
            key.JumpFar(0.2)
            key.PressKey(keycode.up)
            time.sleep(1.5)
            key.ReleaseKey(keycode.up)
            time.sleep(2)

        # capture
        sh.Start(path)
        time.sleep(0.1)
        
        if shopCount > 5:
            key.DoKey(keycode.down, 0.5)
            key.PressKey(keycode.right)
            time.sleep(0.1)
            key.DoKey(keycode.alt)
            time.sleep(0.1)
            key.ReleaseKey(keycode.right)
            time.sleep(0.2)
            self.Walk(72, rect_firstFloor)
        
        # exit map
        key.DoKey(keycode.up)
        self.WaitForResponse()


    def DoMapSecondFloor(self, path):
        # enter map
        key.DoKey(keycode.up)
        self.WaitForResponse()

        shopCount = sh.GetFairyShopCount()
        if shopCount > 5:
            # jump right
            key.JumpFar(0.2)
            key.PressKey(keycode.up)
            time.sleep(1.5)
            key.ReleaseKey(keycode.up)
            time.sleep(2)

        # capture
        sh.Start(path)
        time.sleep(0.1)

        if shopCount > 5:
            # jump left
            key.PressKey(keycode.left)
            time.sleep(0.1)
            key.DoKey(keycode.alt)
            time.sleep(1.3)
            key.ReleaseKey(keycode.left)

        # exit map
        key.DoKey(keycode.up)
        self.WaitForResponse()


    def DoMapThirdFloor(self, path):
        # enter map
        key.DoKey(keycode.up)
        self.WaitForResponse(5) # small threshold for third floor (background does not move)

        shopCount = sh.GetFairyShopCount()
        if shopCount > 5:
            # jump right
            key.JumpFar()
            key.JumpFar()
            key.JumpFar()
            key.JumpFar(0.1)
            key.PressKey(keycode.up)
            time.sleep(1.9)
            key.ReleaseKey(keycode.up)
            time.sleep(2)

        # capture
        sh.Start(path)
        time.sleep(0.1)

        if shopCount > 5:
            # jump left
            key.DoKey(keycode.left)
            time.sleep(0.1)
            key.JumpFar()
            key.JumpFar()
            key.JumpFar()
            key.DoKey(keycode.left, 0.8)

            time.sleep(1)
            sh.Click(30, 430)
            time.sleep(0.1)
            if (sh.IsInShop()):
                sh.Start(path)

        # exit map
        key.DoKey(keycode.up)
        self.WaitForResponse()


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
                key.ReleaseKey(keycode.left)
                key.PressKey(keycode.right)
            elif xdiff > 70:
                key.ReleaseKey(keycode.right)
                key.PressKey(keycode.left)
            else:
                key.ReleaseKey(keycode.left)
                key.ReleaseKey(keycode.right)
                if xdiff < 0:
                    key.DoKey(keycode.right, 0.1)
                elif xdiff > 0:
                    key.DoKey(keycode.left, 0.1)


    def Walk(self, target, rect=rect_entry):
        self.goodCount = 0
        while True:
            scr = sh.Grab(rect)
            scr = scr[:,:,:3]

            result = cv2.matchTemplate(scr, hero_img, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            self.hero_x = max_loc[0]

            if self.WalkTo(target):
                print("arrive")
                break


    def NextChannel(self, num=1):
        key.SetFocus(hwnd)
        key.DoKey(keycode.esc)
        time.sleep(0.1)
        key.DoKey(keycode.enter)
        for i in range(1,num+1):
            time.sleep(0.1)
            key.DoKey(keycode.right)
        time.sleep(0.1)
        key.DoKey(keycode.enter)


    def DoChannel(self, channel):
        key.SetFocus(hwnd)

        for i in range(1,7):
            self.Walk(firstFloor[i])
            self.DoMapFirstFloor(str(channel)+'-'+str(i))

        if str(channel) == "1":
            self.Walk(firstFloor['up'])
            key.DoKey(keycode.up)
            time.sleep(1)
            key.DoKey(keycode.up)

            for i in range(13,18):
                self.Walk(secondFloor[i])
                self.DoMapSecondFloor(str(channel)+'-'+str(i))

            self.Walk(secondFloor['up'])
            key.DoKey(keycode.up)

            for i in range(18,23):
                self.Walk(thirdFloor[i])
                self.DoMapThirdFloor(str(channel)+'-'+str(i))


    def FullCapture(self):
        for i in range(1, 4):
            self.DoChannel(i)
            self.NextChannel()
            self.WaitForResponse()

        self.DoChannel(4)
        self.NextChannel(2)
        self.WaitForResponse()
        self.DoChannel(6)

print("start full capture")

auto = Automator()
auto.FullCapture()
