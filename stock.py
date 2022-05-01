#!/usr/bin/python
# -*- coding: utf-8 -*-

from timer import *
from stock_period import *
from strategy import *

class Stock():
    def __init__(self, stock_number, period, date_str, money):
        self.stock_number  = stock_number
        self.period = period
        self.date_str = date_str

        self.all_data = []
        self.minute_data = []
        self.predict_data = []

        self.stk_prd = {}
        self.predict_result = {}
        self.last_price = 0
        self.last_volume = 0
        for minutes in period:
            self.stk_prd[str(minutes)] = Stock_Period(stock_number, minutes, self.date_str)
            self.last_price = self.stk_prd[str(minutes)].get_last_price()
            self.current_price = self.last_price
            self.predict_result[str(minutes)] = self.stk_prd[str(minutes)].get_predict()

        self.timer = Timer(self.last_price, date_str)
        #self.date_str = self.timer.get_date_str()

        self.money = money
        self.strategy = Strategy(stock_number, self.date_str, money)

        self.end_process = 0

    def push(self, original_data):

        if self.end_process == 1:
            print('end_process')
            return 1

        if original_data['z'] != '-':
            self.current_price = float(original_data['z'])

        #這邊加入all_data
        self.add_all_data(original_data)

        write_data, time_wrong, time_end, data = self.timer.check(original_data)
        while time_wrong == 1:
            print('時間: ' + data['time'].strftime('%Y-%m-%d %H:%M'))
            print('資料時間錯誤 -> 直接跳過')
            print()
            for minutes in self.period:
                self.stk_prd[str(minutes)].push(data)
            write_data, time_wrong, time_end, data = self.timer.check(original_data)
        
        if write_data == 1:
            #加入每分鐘資料
            self.add_minute_data(data)

            tech = {}
            for minutes in self.period:
                self.predict_result[str(minutes)], tech[str(minutes)] = self.stk_prd[str(minutes)].push_and_predict(data)

            self.add_predict_data(self.predict_result, data['time'])

            self.last_price = data['price']
            self.last_volume = data['volume']
            #包裝策略資料
            strategy_data = {
                'time' : data['time'],
                'original' : data['price'],
                '1min' : self.predict_result['1'],
                '5min' : self.predict_result['5'],
                '10min' : self.predict_result['10'],
                'volume' : data['volume'],
                'MA5' : tech['1']['MA5'],
                'avg_price' : tech['1']['avg price'] 
            }
            self.strategy.push(strategy_data)

            #self.print_result(self.predict_result, data['time'], data['price'])
            #self.write_result(predict_result, data['time'], screen, screen_start, col)
        
        if time_end == 1:
            self.end_process = 1
            print('time_end')
            self.strategy.overview()
            self.write_minute_data()
            self.write_all_data()
            self.write_predict_data()

        #已經取得13:30的資料時回傳1
        return time_end 

    def write_result(self, predict_result, time, screen, screen_start, col):
        screen.addstr(screen_start, 0, '資 料 時 間 : ' + time.strftime('%Y-%m-%d %H:%M'))
        screen.addstr(screen_start + 1, (col)*15, self.stock_number)

        for minutes,i in zip(self.period, range(0,len(self.period))):
            screen.addstr(screen_start+i+2, (col)*15, str(minutes) + 'min: ' + str(np.round(predict_result[str(minutes)],2)))
        screen.refresh()
            
    def print_result(self, predict_result, time, price):
        print('時間: ' + time.strftime('%Y-%m-%d %H:%M'))
        print(self.stock_number + '預測結果：')
        print('原價:' ,float(int(price * 100) / 100))
        for minutes in self.period:
            print(str(minutes) + 'min: ' , float(int(predict_result[str(minutes)]*100)/100))
        print()

    def write_excel_file(self, array, file_path, sheet_name, fieldnames):
        if os.path.isfile(file_path):
            wb = openpyxl.load_workbook(file_path)
            if sheet_name in wb.sheetnames:
                sheets = wb[sheet_name]
                wb.remove(sheets)
            wb.create_sheet(sheet_name)
            sheets = wb[sheet_name]
        else:
            wb = openpyxl.Workbook()
            sheets = wb.active
            sheets.title = sheet_name

        sheets.append(fieldnames)
        for row in array:
            #data = [row[col] for col in fieldnames]
            data = []
            for col in fieldnames:
                if col in row:
                    data.append(row[col])
                else:
                    data.append('-')
            sheets.append(data)

        wb.save(file_path)

    def add_predict_data(self, data, time):
        time_str = time.strftime('%H:%M')
        data['time'] = time_str
        self.predict_data.append(data)

    def add_minute_data(self,data):
        time_str = data['time'].strftime('%H:%M')
        format_data = {'資料時間':time_str, '當前成交價':data['price'], '此分鐘成交量':data['volume'], '累積成交量':data['sum_volume']}
        self.minute_data.append(format_data)

    def add_all_data(self, data):
        if data not in self.all_data:
            self.all_data.append(data)

    def write_predict_data(self):
        folder = 'minute predict'
        self.make_dir(folder)
        filename = '{}/{}-{}-result.xlsx'.format(folder, self.date_str, self.stock_number)
        fieldnames = []
        fieldnames.append('time')
        for minutes in self.period:
            title = str(minutes)
            fieldnames.append(title)

        self.write_excel_file(self.predict_data, filename, self.stock_number, fieldnames)

    def write_minute_data(self):
        folder = 'data'
        self.make_dir(folder)
        date_folder = '{}/{}'.format(folder, self.date_str)
        self.make_dir(date_folder)
        filename = '{}/{}/{}.xlsx'.format(folder, self.date_str, self.stock_number)
        fieldnames = ['資料時間', '當前成交價',	'此分鐘成交量',	'累積成交量']

        self.write_excel_file(self.minute_data, filename, 'Sheet', fieldnames)

    def write_all_data(self):
        folder = 'data'
        self.make_dir(folder)
        date_folder = '{}/{}'.format(folder, self.date_str)
        self.make_dir(date_folder)
        filename = '{}/{}/All_Data.xlsx'.format(folder, self.date_str)
        
        fieldnames = []
        for col in self.all_data[0]:
            fieldnames.append(col)

        self.write_excel_file(self.all_data, filename, self.stock_number, fieldnames)

    def make_dir(self, folder):
        if not os.path.isdir(folder):
            os.mkdir(folder)

    def get_data(self):
        data = {
            '股票編號' : self.stock_number,
            '上分鐘價錢' : self.last_price,
            '上分鐘成交量' : self.last_volume,
            '目前價錢' : self.current_price,
            '本金' : self.money,
            '剩餘金額' : self.strategy.get_left_money(),
            '持股張數' : self.strategy.get_lot_num(),
            '報酬率' : self.strategy.get_return_rate()
        }
        for minutes in self.period:
            data[str(minutes) + '分鐘後'] = self.predict_result[str(minutes)]
        return data

    def get_strategy_detail(self):
        return self.strategy.get_detail_view()
        
        

'''
stock_number = '00637L'
period = [1,5,10]
s = Stock(stock_number,period)
s.push({"tv":"552","ps":"551","nu":"http://www.yuantaetfs.com/#/RtNav/Index","pz":"20.5800","bp":"0","fv":"19","oa":"20.8000","ob":"20.6800","a":"20.5900_20.6000_20.6100_20.6200_20.6300_","b":"20.5800_20.5700_20.5600_20.5500_20.5400_","c":"00637L","d":"20210917","ch":"00637L.tw","ot":"14:30:00","tlong":"1631860200000","f":"32_41_17_992_930_","ip":"0","g":"406_751_955_1299_1435_","mt":"000000","ov":"457","h":"20.6900","it":"02","oz":"20.6800","l":"19.9500","n":"元大滬深300正2","o":"20.1800","p":"0","ex":"tse","s":"552","t":"13:30:00","u":"9999.9500","v":"44894","nf":"元大滬深300傘型證券投資信託基金之滬深300單日正向2倍證券投資信託基金","y":"20.2600","z":"20.5800","ts":"0"})
'''
