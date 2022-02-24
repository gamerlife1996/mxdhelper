from key import SetFocus, PressKey, ReleaseKey
import time
import win32gui
import capture

import win32gui

window_handle = win32gui.FindWindow("MapleStoryClass", None)
window_rect   = win32gui.GetWindowRect(window_handle)

hwnd = win32gui.FindWindow("MapleStoryClass", None)

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
    time.sleep(2)

    shopCount = sh.GetFairyShopCount()
    if shopCount > 5:
        # jump left
        DoKey(keycode.left)
        time.sleep(0.1)
        JumpFar()

        # climb stairs
        PressKey(keycode.right)
        DoKey(keycode.alt)
        time.sleep(0.75)
        DoKey(keycode.alt)
        time.sleep(1.0)
        ReleaseKey(keycode.right)
    
        # jump to bring camera up
        time.sleep(0.2)
        DoKey(keycode.alt)
        time.sleep(0.5)

    # capture
    sh.Start(path)
    time.sleep(0.1)
    
    if shopCount > 5:
        # jump down
        PressKey(keycode.down)
        time.sleep(0.1)
        DoKey(keycode.alt)
        time.sleep(0.1)
        ReleaseKey(keycode.down)
        time.sleep(1)
    
    # exit map
    DoKey(keycode.up)
    time.sleep(3)

def FirstFloor(channel):
    DoMapFirstFloor(str(channel) + '-1')
    DoKey(keycode.right, 1)
    DoMapFirstFloor(str(channel) + '-2')
    DoKey(keycode.right, 1)
    DoMapFirstFloor(str(channel) + '-3')
    DoKey(keycode.right, 1.4)
    DoMapFirstFloor(str(channel) + '-4')
    DoKey(keycode.right, 1.2)
    DoMapFirstFloor(str(channel) + '-5')
    DoKey(keycode.right, 1.2)
    DoMapFirstFloor(str(channel) + '-6')

def DoMapSecondFloor(path):
    # enter map
    DoKey(keycode.up)
    time.sleep(2)

    # jump right
    JumpFar(0.2)
    PressKey(keycode.up)
    time.sleep(1.5)
    ReleaseKey(keycode.up)
    time.sleep(2)

    # capture
    sh.Start(path)
    time.sleep(0.1)

    # jump left
    PressKey(keycode.left)
    time.sleep(0.1)
    DoKey(keycode.alt)
    time.sleep(1.3)
    ReleaseKey(keycode.left)

    # exit map
    DoKey(keycode.up)
    time.sleep(3)

def SecondFloor(channel):
    DoMapSecondFloor(str(channel) + '-13')
    DoKey(keycode.right, 1.1)
    DoMapSecondFloor(str(channel) + '-14')
    DoKey(keycode.right, 1.1)
    DoMapSecondFloor(str(channel) + '-15')
    DoKey(keycode.right, 1.2)
    DoMapSecondFloor(str(channel) + '-16')
    DoKey(keycode.right, 1.1)
    DoMapSecondFloor(str(channel) + '-17')

def DoMapThirdFloor(path):
    # enter map
    DoKey(keycode.up)
    time.sleep(2)

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
    time.sleep(3)

def ThirdFloor(channel):
    DoMapThirdFloor(str(channel) + '-18')
    DoKey(keycode.right, 1)
    DoMapThirdFloor(str(channel) + '-19')
    DoKey(keycode.right, 1)
    DoMapThirdFloor(str(channel) + '-20')
    DoKey(keycode.right, 1)
    DoMapThirdFloor(str(channel) + '-21')
    DoKey(keycode.right, 1)
    DoMapThirdFloor(str(channel) + '-22')


def KeyPress():
    SetFocus(hwnd)

    # FirstFloor(channel=1)
    # SecondFloor(channel=1)
    # ThirdFloor(channel=1)
    # FirstFloor(channel=2)
    # FirstFloor(channel=3)
    # DoMapFirstFloor('4-1')
    DoMapFirstFloor('6-1')


KeyPress()