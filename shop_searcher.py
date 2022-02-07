import os
import json
import re

from tkinter import *
from tkinter import filedialog
from tkinter import PhotoImage
from tkinter.ttk import Style
from tkinter.ttk import Treeview

from PIL import ImageTk, Image

class shop_seacher():
    
    def __init__(self):
        self.window = Tk()
        self.window.title("商店搜索器 v1.2")
        self.window.geometry("1365x500")

        
        frame_left = Frame(self.window)
        frame_right = Frame(self.window)

        self.display_img = Label(frame_right)
        self.display_img.grid(column=0, row=0)

        frame_top = Frame(frame_left)

        self.keywords_2_vert_json = {}
        self.keywords_2_frag_json = {}
        
        load_button = Button(frame_top,text="加载数据",command=self.load_data)
        load_button.grid(column=0, row=0)

        self.chk_state = BooleanVar()
        self.chk_state.set(False)
        chk = Checkbutton(frame_top, text="只显示有货", var=self.chk_state, command=self.refresh_tree)
        chk.grid(column=1, row=0)

        self.chk_fuzzy = BooleanVar()
        self.chk_fuzzy.set(True)
        chk = Checkbutton(frame_top, text="模糊搜索", var=self.chk_fuzzy, command=self.refresh_tree)
        chk.grid(column=2, row=0)

        search_lbl = Label(frame_top,text="搜索：")
        search_lbl.grid(column=3, row=0)
        self.search_txt = Entry(frame_top, width=80)
        self.search_txt.grid(column=4, row=0)
        self.search_txt.bind("<Return>", lambda e:(self.refresh_tree()))

        self.lbl_count = Label(frame_top,text="数量：0")
        self.lbl_count.grid(column=5, row=0)

        frame_top.grid(row=0, column=0, sticky=W+E)

        frame = Frame(frame_left, padx=5, pady=5)
        frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky=E+W+N+S)
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(2, weight=1)

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.tree = Treeview(frame,column=('截图','名字','价格','商店', '位置', '有货', '时间'))
        self.tree.bind("<<TreeviewSelect>>", self.OnTreeClick)
        self.tree.heading('#0', text='截图', anchor='center')
        self.tree.heading('#1', text='名字', anchor='center')
        self.tree.heading('#2', text='价格', anchor='center')
        self.tree.heading('#3', text='商店', anchor='center')
        self.tree.heading('#4', text='位置', anchor='center')
        self.tree.heading('#5', text='有货', anchor='center')
        self.tree.heading('#6', text='时间', anchor='center')
        self.tree.column('#0', anchor='center', width=220)
        self.tree.column('#1', anchor='center', width=150)
        self.tree.column('#2', anchor='center', width=150)
        self.tree.column('#3', anchor='center', width=280)
        self.tree.column('#4', anchor='center', width=50)
        self.tree.column('#5', anchor='center', width=50)
        self.tree.column('#6', anchor='center', width=130)

        s = Style()
        s.configure('Treeview', rowheight=40)

        self.tree.grid(row=0,column=0,sticky=E+W+N+S)

        scroll = Scrollbar(frame, orient='vertical', command=self.tree.yview)
        scroll.grid(row=0,column=1,sticky=E+N+S)
        self.tree.configure(yscrollcommand=scroll.set)

        frame_left.grid(row=0, column=0, sticky=W+N+S)
        frame_right.grid(row=0, column=1, sticky=E+N+S)

        self.window.mainloop()
        
        
    def OnTreeClick(self, arg):
        iid = self.tree.focus()
        if iid in self.id2map:
            mapname = self.id2map[iid]
            index = self.id2index[iid]
            if index in self.map2img_detail[mapname]:
                img = self.map2img_detail[mapname][index]
                self.display_img.configure(image=img)
                self.display_img.image = img
            else:
                self.display_img.configure(image='')
        else:
            self.display_img.configure(image='')


    def load_data(self):
        filepath = os.path.realpath(__file__)
        folder = filepath[:filepath.rindex('\\')]
        dir = filedialog.askdirectory(initialdir=folder)
        if len(dir) == 0:
            return

        self.map2json = {}
        self.map2img = {}
        self.map2img_detail = {}
        
        maps = os.listdir(dir)
        for map in maps:
            with open(dir+"/"+map+"/json.txt", mode='r', encoding='utf-8') as file:
                json_text = file.read()
            shop_json = json.loads(json_text)

            self.map2json[map] = shop_json
            self.map2img[map] = {}
            self.map2img_detail[map] = {}
            
            for shop in shop_json['shops']:
                for item in shop['goods']:
                    index = item['index']
                    self.map2img[map][index] = ImageTk.PhotoImage(Image.open(dir+"/"+map+"/"+str(index)+".jpg"))
                    detail_path = dir+"/"+map+"/"+str(index)+"_detail.jpg"
                    if os.path.exists(detail_path):
                        self.map2img_detail[map][index] = ImageTk.PhotoImage(Image.open(detail_path))

        self.refresh_tree()

    def refresh_tree(self):
        search = self.search_txt.get().strip()
    
        if len(self.map2json) == 0:
            return

        self.id2map = {}
        self.id2index = {}
        self.tree.delete(*self.tree.get_children())

        for map,json in self.map2json.items():
            for shop in json['shops']:
                for item in shop['goods']:
                    if len(search) > 0:
                        pattern = ".*"+search+".*" if self.chk_fuzzy.get() else "^"+search+"$"
                        ret = re.match(pattern, item['name'])
                        if ret == None:
                            continue
                    
                    if self.chk_state.get() == True and item['available'] == False:
                            continue
                        
                    tree_item_value = (item['name'], item['price'], shop['title'], map, item['available'], json['time'])
                    iid = self.tree.insert('', 'end', text='', image=self.map2img[map][item['index']], value=tree_item_value)
                    self.id2map[iid] = map
                    self.id2index[iid] = item['index']
        
        self.lbl_count.configure(text="数量：" + str(len(self.tree.get_children())))

shop_seacher()