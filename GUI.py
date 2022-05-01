import datetime
import tkinter as tk
import platform
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk

class GUI():
    def __init__(self, stocks, stock_obj):
        self.stocks = stocks
        self.stock_obj = stock_obj

        self.window = tk.Tk()
        self.window.title('Stock')
        self.window.state("zoomed")
        
        align_mode = 'nswe'
        self.pad = 3

        #self.original_width = 1000
        #self.original_height = 600

        #self.w = self.original_width
        #self.h = self.original_height

        self.w = self.window.winfo_screenwidth()
        self.h = self.window.winfo_screenheight()

        self.set_window_size(self.w, self.h)

        self.left_half = tk.Frame(self.window,  width=self.left_half_width , height=self.left_half_height , bg='#F0F0F0')
        self.right_half = tk.Frame(self.window,  width=self.right_half_width , height=self.right_half_height , bg='#F0F0F0')
        
        self.left_half.grid(column=0, row=0, padx=self.pad, pady=self.pad, sticky=align_mode)
        self.right_half.grid(column=1, row=0, padx=0, pady=self.pad, sticky=align_mode)

        self.define_layout(self.window, cols=2)
        self.define_layout([self.left_half, self.right_half])

        self.div1 = tk.Frame(self.left_half,  width=self.time_width , height=self.time_height , bg='#FFD39B')
        self.div2 = tk.Frame(self.left_half,  width=self.info_width , height=self.info_height , bg='#BFEFFF')
        self.div3 = tk.Frame(self.right_half,  width=self.button_zone_width , height=self.button_zone_height , bg='white')#3D313F
        
        self.div1.grid(column=0, row=0, padx=self.pad, pady=self.pad, sticky=align_mode) #顯示時間
        self.div2.grid(column=0, row=1, padx=self.pad, pady=self.pad, sticky=align_mode) #顯示資訊
        self.div3.grid(column=0, row=0, padx=0, pady=self.pad, sticky=align_mode) #顯示按鈕

        self.define_layout(self.left_half, cols=1, rows=2)
        self.define_layout([self.div1, self.div2])

        #window.update()
        #win_size = min( window.winfo_width(), window.winfo_height())
        
        self.set_time_zone(self.div1)
        self.set_button_zone(self.div3)

        self.state = {}
        self.set_table(self.div2)
        #self.stock_detail(self.div2, '00637L')
        

        self.isFullScreen = False
        #self.window.bind('<F12>', self.toggle_fullScreen)
        self.window.bind('<Configure>', self.resize)
        #self.window.bind('<ButtonRelease>', self.get_size)
        self.window.bind('<Escape>', self.del_window)
        self.window.mainloop()
        
    #計算所有物件的大小
    def set_window_size(self, width, height):
        self.window_width = width
        self.window_height = height

        self.right_half_width = 210
        self.right_half_height = self.window_height - (2*self.pad)

        #self.left_half_width = int((self.window_width*8)/10)
        self.left_half_width = self.window_width - self.right_half_width - (2*self.pad)
        self.left_half_height = self.window_height - (2*self.pad)

        self.time_width = self.left_half_width - (2*self.pad)
        self.time_height = 50

        #print(self.time_height)

        self.info_width = self.left_half_width - (2*self.pad)
        #self.info_height = int((self.window_height*12)/13)
        self.info_height = self.left_half_height - self.time_height - (4*self.pad)

        #print(self.info_height)

        #self.button_zone_width = int((self.window_width*2)/10)
        self.button_zone_width = self.right_half_width
        self.button_zone_height = self.right_half_height - (2*self.pad)

        self.button_width = 20#(self.right_half_width/10.5)
        self.button_height = 4

        #self.button_width = self.button_zone_width
        #self.button_height = self.button_width/2

    #這個是別人寫的(分割區塊)
    def define_layout(self, obj, cols=1, rows=1):

        def method(trg, col, row):
            
            for c in range(col):
                trg.columnconfigure(c, weight=0)
            for r in range(row):
                trg.rowconfigure(r, weight=0)

        if type(obj)==list:     
            [ method(trg, cols, rows) for trg in obj ]
        else:
            trg = obj
            method(trg, cols, rows)

    #重新定義視窗大小
    def resize(self, event):
        self.w = self.window.winfo_width()
        self.h = self.window.winfo_height()
        #self.set_window_size(self.w,self.h)

        self.left_half['height'] = self.left_half_height
        self.left_half['width'] = self.left_half_width
        self.right_half['height'] = self.right_half_height
        self.right_half['width'] = self.right_half_width
        
        self.div1['height'] = self.time_height
        self.div1['width'] = self.time_width
        
        self.div2['height'] = self.info_height
        self.div2['width'] = self.info_width

        self.div3['height'] = self.button_zone_height
        self.div3['width'] = self.button_zone_width

    #全螢幕
    def toggle_fullScreen(self, event):
        is_windows = lambda : 1 if platform.system() == 'Windows' else 0

        self.isFullScreen = not self.isFullScreen
        self.window.attributes("-fullscreen" if is_windows() else "-zoomed", self.isFullScreen)
        
    #刪除視窗
    def del_window(self, event):
        self.window.destroy()

    def set_time_zone(self, window):
        time_now = datetime.datetime.now().strftime('%Y/%m/%d    %H:%M:%S')
        txt = 'Time:   ' + time_now

        window.grid_columnconfigure(0, minsize=self.time_width)
        window.grid_rowconfigure(0, minsize=self.time_height)
        #FFD39B
        self.time_label = tk.Label(window, text=txt, bg='#A67F78', fg='black', font=('Times new roman', 16), width=50, height=1)
        self.time_label.grid(column=0, row=0, sticky=S)
        self.time_label.pack(fill='both',  expand=True)

        self.update_time()

    def update_time(self):
        time_now = datetime.datetime.now().strftime('%Y/%m/%d    %H:%M:%S')
        txt = 'Time:   ' + time_now

        self.time_label['text'] = txt
        self.time_label.after(1000, self.update_time)
    
    def tmp_set_table(self, window):
        #pass
        yscroll = Scrollbar(window, orient=VERTICAL)
        columns = self.stocks

        style = ttk.Style()
        #style.theme_use('clam')
        #style.configure('Treeview.Heading', rowheight=50 ,font=('Times new roman', 14), background='#6495ED')#設定表頭
        style.configure('Treeview',rowheight=50,font=('Times new roman', 14) ,background='#BFEFFF')#設定表格內容
        #style.configure('Calendar.Treeview', rowheight=50)
        #style.map('Treeview.Heading', background='#383838')
        style.map('Treeview',foreground=[('selected', 'blue')] ,background=[('selected', '#BFEFFF')])

        self.table = ttk.Treeview(
            master=window,  # 父容器
            #height=10,  # 表格顯示的行数,height行
            columns=columns,  # 显示的列
            #show='headings',  # 隐藏首列
            show='tree',  # 隐藏首列
            yscrollcommand=yscroll.set,  # y轴滚动条
        )
        
        self.table.heading('#0', text='股票編號', anchor='center')
        self.table.column(column='#0', width = 150, minwidth=100 , anchor='center')
        for column in columns:
            self.table.heading(column=column, text=column, anchor='center')  # 定義表頭
            self.table.column(column=column, width = 150, minwidth=100 , anchor='center')  # 定義列

        self.table.tag_configure('first_column', background='orange')
        self.table.tag_configure('other_column', background='purple')
        
        yscroll.config(command=self.table.yview)
        yscroll.pack(side=RIGHT, fill=Y)
        #table.pack(fill=BOTH, expand=True)
        self.table.pack(side=LEFT, fill=Y, expand=True)

        data = ['123', '456', 'asd', 'vvv']
        self.table.insert(parent='', index=END, text='股票編號', values=self.stocks, tags='first_column')
        self.table.insert(parent='', index=END, text='上分鐘價錢', values=data)
        self.table.insert(parent='', index=END, text='上分鐘成交量', values=data)

    def tmp2_set_table(self, window):
        
        self.table={}
        self.table['frame'] = tk.Frame(window, background='green')
        self.table['frame'].pack()

        scrollbar = Scrollbar(self.table['frame'], orient=VERTICAL)
        scrollbar.grid(row=0, column=1, sticky=N+S)
        #scrollbar.pack(side="right",fill="y")
        
        #scrollbar=Scrollbar(self.table['frame'], orient="vertical")
        #scrollbar.pack(side="right",fill="y")

        self.info_title = self.create_label(self.table['frame'], 'Overview', 0, 0, '#BFEFFF', 'black', len(self.stocks)+1)
        #self.info_title.pack(fill='x')
        self.info_title.grid(row=0, column=0)

        self.table['1']=tk.Frame(self.table['frame'])
        self.table['2']=tk.Frame(self.table['frame'])
        self.table['3']=tk.Frame(self.table['frame'])

        #self.table['1'].pack()
        #self.table['2'].pack()
        #self.table['3'].pack()

        self.table['1'].grid(row=1, column=0)
        self.table['2'].grid(row=2, column=0)
        self.table['3'].grid(row=3, column=0)

        self.create_table(self.table['1'], '基本資訊', ['股票編號', '上分鐘價錢', '上分鐘成交量', '目前價錢'])
        self.create_table(self.table['2'], '預測', ['1分鐘後', '5分鐘後', '10分鐘後'])
        self.create_table(self.table['3'], '策略總覽', ['本金', '剩餘金額', '持股張數', '報酬率'])

        #self.table['frame'].config(yscrollcommand=scrollbar.set)
        #scrollbar.config(command=self.table['frame'].yview)

    #用canvas當scrollbar
    def set_table(self, window):
        
        self.table={}
        #aqua
        self.table['canvas'] = tk.Canvas(window, background='#847072',width=self.info_width,height=self.info_height,scrollregion=(0,0,self.info_width,1000))
        
        scrollbar = Scrollbar(self.table['canvas'], orient=VERTICAL)
        scrollbar.pack(side="right",fill="y")
        scrollbar.configure(command=self.table['canvas'].yview)

        #scrollbar.grid(row=0, column=1, sticky=N+S)
        #scrollbar.pack(side="right",fill="y")
        self.table['frame'] = tk.Frame(self.table['canvas'], background='#847072')
        self.table['frame'].pack()

        self.table['canvas'].config(yscrollcommand=scrollbar.set)
        self.table['canvas'].pack(side=LEFT,expand=True,fill=BOTH)
        self.table['canvas'].create_window((self.info_width/2,470),window=self.table['frame'])
        
        
        self.info_title = self.create_label(self.table['frame'], 'Overview', 0, 0, '#847072', 'black', len(self.stocks)+1, 'flat')
        #self.info_title.pack(fill='x')
        self.info_title.grid(row=0, column=0)

        self.table_contain = {}
        for stock in self.stocks:
            self.table_contain[stock] = {}

        self.table['1']=tk.Frame(self.table['frame'])
        self.table['2']=tk.Frame(self.table['frame'])
        self.table['3']=tk.Frame(self.table['frame'])

        #self.table['1'].pack()
        #self.table['2'].pack()
        #self.table['3'].pack()

        self.table['1'].grid(row=1, column=0)
        self.table['2'].grid(row=2, column=0)
        self.table['3'].grid(row=3, column=0)

        self.create_table(self.table['1'], '基本資訊', ['股票編號', '上分鐘價錢', '上分鐘成交量', '目前價錢'])
        self.create_table(self.table['2'], '預測', ['1分鐘後', '5分鐘後', '10分鐘後'])
        self.create_table(self.table['3'], '策略總覽', ['本金', '剩餘金額', '持股張數', '報酬率'])

        self.state['Overview'] = self.table['canvas']
        
        #self.table['frame'].config(yscrollcommand=scrollbar.set)
        #scrollbar.config(command=self.table['frame'].yview)
        
        self.update_overview_info()
    
    def stock_detail(self, window, stock):

        self.info={}
        self.info['canvas'] = tk.Canvas(window, background='#847072',width=self.info_width,height=self.info_height,scrollregion=(0,0,self.info_width,1000))
        self.state[stock] = self.info['canvas']

        scrollbar = Scrollbar(self.info['canvas'], orient=VERTICAL)
        scrollbar.pack(side="right",fill="y")
        scrollbar.configure(command=self.info['canvas'].yview)

        self.info['frame'] = tk.Frame(self.info['canvas'], background='#847072')
        self.info['frame'].pack()

        self.info['canvas'].config(yscrollcommand=scrollbar.set)
        self.info['canvas'].pack(side=LEFT,expand=True,fill=BOTH)
        #self.info['canvas'].create_window((self.info_width/2,100),window=self.info['frame'])
        self.info['canvas'].create_window(((self.info_width/2)-400,20),window=self.info['frame'], anchor=N+W)

        self.info_title = self.create_label(self.info['frame'], stock, 0, 0, '#847072', 'black', 6, 'flat')
        #self.info_title.pack(fill='x')
        self.info_title.grid(row=0, column=0)

        self.info['table'] = tk.Frame(self.info['frame'])
        self.info['table'].grid(row=1, column=0)

        field_names = ['時間','買入張數','買入價格','賣出張數','賣出價格','持有張數']
        self.create_strategy_table(self.info['table'], stock, field_names)

        self.update_stock_info()

    def create_strategy_table(self, window, stock ,fields):
        view = self.stock_obj[stock].get_strategy_detail()
        for (field,j) in zip(fields, range(0, 100)):
            self.create_label(window, field, 0, j, '#DCC1B0', '#404040', 1, 'groove')
        
        for (row,i) in zip(view, range(1, 100)):
            for (field,j) in zip(fields, range(0, 100)):
                self.create_label(window, row[field], i, j, '#DCC1B0', '#525252', 1, 'groove')

    def create_table(self, window, title, fields):
        self.create_label(window, title, 0, 0, '#607178', '#404040', len(self.stocks)+1, 'groove')
        for field,i in zip(fields, range(1,100)):
            self.create_label(window, field, i, 0, '#607178', '#404040', 1, 'groove')
            for stock,j in zip(self.stocks,range(1,100)):
                self.table_contain[stock][field] = self.create_label(window, stock, i, j, '#DCC1B0', 'black', 1, 'groove')
        
    def create_label(self, window, txt, row, col, bg_color, fg_color, size, relief):
        lbl = tk.Label(window, text=str(txt), bg=bg_color, fg=fg_color, font=('Times new roman', 12), width=size*15, height=3, relief=relief,borderwidth=1)
        lbl.grid(column=col, row=row, columnspan=size, sticky=W+E)
        #lbl.pack(fill=X,  expand=True)
        return lbl
    
    def update_overview_info(self):
        for stock in self.stocks:
            data = self.stock_obj[stock].get_data()
            for field in data:
                self.table_contain[stock][field]['text'] = str(data[field])
        self.table['frame'].after(1000, self.update_overview_info)

    def update_stock_info(self):
        self.info['table'].destroy()
        self.info['table'] = tk.Frame(self.info['frame'])
        self.info['table'].grid(row=1, column=0)

        field_names = ['時間','買入張數','買入價格','賣出張數','賣出價格','持有張數']
        self.create_strategy_table(self.info['table'], self.button_state, field_names)
        
        self.info['table'].after(1000, self.update_stock_info)
        

    def set_button_zone(self, window):
        self.button_state = 'Overview'
        self.btn_list = {}
        self.btn_list['Overview'] = self.create_button('Overview', window, 0)
        for stock,index in zip(self.stocks,range(1,100)):
            self.btn_list[stock] = self.create_button(stock, window, index)

    #新增按鈕
    def create_button(self, txt, div, row):
        btn = tk.Button(div, text=txt, bg='#8F8681', fg='white',  font=('Times new roman', 14), width = self.button_width, height = self.button_height)
        #pixelVirtual = tk.PhotoImage(width=1, height=1)
        #btn = tk.Button(div, text=txt, image=pixelVirtual,compound='c',bg='#EEB422', fg='white',  font=('Times new roman', 14), width = self.button_width, height = self.button_height)
        btn.grid(column=0, row=row, sticky='N')
        #btn['width'] = 20
        #btn['height'] = 15
        btn['activebackground'] = '#BFEFFF'  
        btn['activeforeground'] = 'black' 
        btn['command'] = lambda:self.button_command(txt)
        return btn

    def button_command(self,txt):
        self.state[self.button_state].destroy()
        self.button_state = txt
        if txt == 'Overview':
            self.set_table(self.div2)
        else:
            self.stock_detail(self.div2, txt)
        

'''
a = 0
stock = ['00637L', '2454', '2330', '3665']
GUI(stock, a)
'''
