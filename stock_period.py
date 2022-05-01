#!/usr/bin/python
# -*- coding: utf-8 -*-

from technical_calculator import *
from lstm import *
import openpyxl

class Stock_Period():
    def __init__(self, stock_number, period, date_str):
        self.number = stock_number
        self.period = period
        self.counter = 0
        self.date_str = date_str

        #讀取上一筆資料
        self.filename = '{}/{}-{}min.csv'.format('synthesis data', stock_number, self.period)
        data = pd.read_csv(self.filename, encoding= 'unicode_escape', index_col='Date & Time', parse_dates = {'Date & Time':[0,1]})

        #確認有沒有昨天的資料並取得最後一筆的時間跟價錢
        last_time, self.last_price = self.check_date(data)

        #丟給算技術指標的物件
        self.tech = Technical_Calculator(data.tail(30).copy(), last_time, period)
        self.lstm_model = LSTM_model(stock_number, period)

        #取得第一分鐘預測價格
        predict, correction = self.lstm_model.predict_and_correction(data.tail(20))
        self.correction = float(int(correction * 100)) / 100

        self.volume = 0

    def check_date(self,data):
        idx = data.tail(1).index
        time = idx[0]
        data_date_str = time.strftime('%Y%m%d')
        #today_date_str = datetime.datetime.today().strftime('%Y%m%d')
        close = file_to_array('close.xlsx')
        last_date_str = last_date(self.date_str, close)
        if data_date_str != last_date_str:
            print('缺乏 ' + self.number + ':' + str(self.period) + '分鐘的資料')
            exit(0)############################################################
        return time, data.loc[time]['Current Price']

    def push(self,data): #時間錯誤只呼叫push，不預測
        self.volume = self.volume + data['volume']
        if self.counter % self.period == 0:
            predict_data = self.tech.push(data['price'], data['volume'], data['time'])
            self.volume = 0
        self.counter = self.counter + 1
    

    def push_and_predict(self,data): #data = {time,price,volume} 無論period每分鐘丟入一筆
        self.volume = self.volume + data['volume']
        if self.counter % self.period == 0:
            predict_data, time = self.tech.push(data['price'], self.volume, data['time'])
            self.volume = 0
            predict, correction = self.lstm_model.predict_and_correction(predict_data)
            #四捨五入
            self.correction = float(int(correction * 100)) / 100
        self.counter = self.counter + 1
        return self.correction, self.tech.get_last_data()

    
    def get_last_price(self):
        return self.last_price

    def get_data(self):
        return self.tech.get_data()

    def get_predict(self):
        return self.correction

def last_date(str_today, close):
    today = datetime.datetime.strptime(str_today, '%Y%m%d')
    oneday = datetime.timedelta(days=1) 
    
    weekday = today.weekday() + 1
    if weekday == 1:
        last_date = today - (oneday * 3)
    elif weekday == 7:
        last_date = today - (oneday * 2)
    else:
        last_date = today - oneday
    str_last = last_date.strftime('%Y%m%d')

    while str_last in close:
        last_date = datetime.datetime.strptime(str_last, '%Y%m%d')
        weekday = last_date.weekday() + 1
        if weekday == 1:
            last_date = last_date - (oneday * 3)
        elif weekday == 7:
            last_date = today - (oneday * 2)
        else:
            last_date = last_date - oneday
        str_last = last_date.strftime('%Y%m%d')
    
    return str_last

def file_to_array(file):
    workbook = openpyxl.load_workbook(file)
    sheets = workbook.sheetnames
    booksheet = workbook[sheets[0]] 
    rows = booksheet.rows

    array = []
    for row in rows:
        line=[col.value for col in row]
        array.append(str(line[0]))
    return array

'''
#用來測試Stock_period
s = Stock_Period('00637L',1)
time = datetime.datetime.strptime(str(datetime.datetime.now().date())+' 9:00', '%Y-%m-%d %H:%M')
data = {'time':time,'price':35.7,'volume':55}
c = s.push_and_predict(data)
print(c)
'''
