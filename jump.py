import cv2
import time
import json
import sys
import os
from tesserocr import PyTessBaseAPI, RIL, iterate_level, PSM
from PIL import Image
import shutil
import numpy
import mss
import win32gui
import key
from key import keycode

window_handle = win32gui.FindWindow("MapleStoryClass", None)
window_rect   = win32gui.GetWindowRect(window_handle)

hair_img = cv2.imread('source/hair.png')
hero_img = cv2.imread('source/hero.png')

sct = mss.mss()

def Match(scr, source):
    result = cv2.matchTemplate(scr, source, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    return max_val, max_loc

def MatchFlip(scr, source):
    val, loc = Match(scr, source)
    if val > 0.9:
        return loc
    val, loc = Match(scr, cv2.flip(source, 1))
    if val > 0.9:
        return loc

jump_left_pos = [(88, 178), (71, 178), (65, 174), (49, 178), (37, 178)]
jump_up_pos = [(32, 174)]
jump_right_pos = [(20, 163), (43, 163), (60, 163), (61, 163), (76, 163), (88, 159)]

def WalkBottomFloor():
    key.SetFocus(window_handle)

    loc = (0, 0)
    while True:
        scr = numpy.array(sct.grab(window_rect))
        scr = scr[:,:,:3]

        last_loc = loc
        val, loc = Match(scr, hero_img)
        diff = (loc[0] - last_loc[0], loc[1] - last_loc[1])
        print(loc, diff)

        if loc[0] > 36 and loc[1] > 170:
            key.ReleaseKey(keycode.right)
            key.PressKey(keycode.left)
        if loc[0] >= 30 and loc[1] == 159:
            key.PressKey(keycode.right)

        if loc in jump_left_pos:
            print("jump")
            key.DoKey(keycode.alt)
        elif loc in jump_right_pos:
            print("jump")
            key.DoKey(keycode.alt)
        elif loc in jump_up_pos:
            key.DoKey(keycode.alt)
        
        if loc[0] < 36 and loc[1] > 170:
            key.ReleaseKey(keycode.left)
        if loc[0] > 88 and loc[1] < 160 and loc[1] > 150:
            key.ReleaseKey(keycode.right)

        if loc == (33, 174):
            key.DoKey(keycode.alt)
        if diff[1] == 0 and loc == (33, 170) or loc == (32, 170):
            key.JumpLeft(0.3)
        if diff[1] == 0 and loc == (27, 167) or loc == (28, 167):
            key.JumpLeft(0.4)
        if diff[1] == 0 and loc == (22, 163) or loc == (21, 163):
            key.JumpRight()
        if diff[1] == 0 and loc == (25, 159) or loc == (26, 159):
            key.JumpRight()
            
        if diff[1] == 0 and loc == (93, 155):
            key.JumpRight(0.3)

        cv2.




WalkBottomFloor()

# key.SetFocus(window_handle)
# key.DoKey(keycode.alt)
# time.sleep(1)
# key.DoKey(keycode.left, 0.2)
# key.JumpLeft(0.3)
# key.DoKey(keycode.left, 0.2)
# key.JumpRight(0.3)
# time.sleep(0.5)
# key.JumpRight(0.3)
