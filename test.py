import tesserocr
from PIL import Image
import time
import cv2
import numpy
from tesserocr import PyTessBaseAPI, RIL, iterate_level, PSM

# name = cv2.imread('name.png')
# enlarge = cv2.resize(name, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
# threshold = cv2.threshold(enlarge, 128, 255, cv2.THRESH_BINARY)[1]

# img = Image.fromarray(threshold)

print(time.time())

time_start = time.perf_counter()

# print("result",tesserocr.image_to_text(img))

with PyTessBaseAPI(lang='chi_my', psm=PSM.SINGLE_LINE) as api:
    api.SetImageFile('test.png')
    text = api.GetUTF8Text()
    print("result",text)

# with PyTessBaseAPI() as api:
#     api.SetImageFile('test.png')
#     api.Recognize()
#     allConfs = api.AllWordConfidences()
#     print('allconfs',allConfs)
#     boxes = api.GetComponentImages(RIL.TEXTLINE, True)
#     print('Found {} textline image components.'.format(len(boxes)))
#     for i, (im, box, _, _) in enumerate(boxes):
#         # im is a PIL image object
#         # box is a dict with x, y, w and h keys

#         img = numpy.array(im)
#         cv2.imshow("im",img)
#         cv2.waitKey(0)

#         api.SetRectangle(box['x'], box['y'], box['w'], box['h'])
#         ocrResult = api.GetUTF8Text()
#         conf = api.MeanTextConf()
#         print('conf', conf)
#         print(u"Box[{0}]: x={x}, y={y}, w={w}, h={h}, "
#               "confidence: {1}, text: {2}".format(i, conf, ocrResult, **box))

# with PyTessBaseAPI(lang='chi_sim', psm=PSM.OSD_ONLY) as api:
#     api.SetImageFile('test.png')

#     os = api.DetectOS()
#     print(os)
#     print("Orientation: {orientation}\nOrientation confidence: {oconfidence}\n"
#           "Script: {script}\nScript confidence: {sconfidence}".format(**os))

# with PyTessBaseAPI(lang='chi_my') as api:
#     api.SetImageFile('test.png')
#     api.SetVariable("save_blob_choices", "T")
#     api.SetVariable("lstm_choice_mode", "2")
#     # api.SetRectangle(0, 0, 123, 36)
#     api.Recognize()

#     print(choices)
#     level = RIL.SYMBOL
#     for r in iterate_level(ri, level):
#         symbol = r.GetUTF8Text(level)  # r == ri
#         conf = r.Confidence(level)
#         if symbol:
#             print(u'symbol {}, conf: {}'.format(symbol, conf), end='')
#         indent = False
#         ci = r.GetChoiceIterator()
#         for c in ci:
#             if indent:
#                 print('\t\t ', end='')
#             print('\t- ', end='')
#             choice = c.GetUTF8Text()  # c == ci
#             print(u'{} conf: {}'.format(choice, c.Confidence()))
#             indent = True
#         print('---------------------------------------------')

time_end = time.perf_counter()
print("time",time_end-time_start)