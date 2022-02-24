from capture import ShopHelper
import sys

if len(sys.argv) < 2:
    print('folder name is empty, default is test.')
    path = 'test'
else:
    path = sys.argv[1]

sh = ShopHelper()
sh.Start(path)