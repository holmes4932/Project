#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

class Timer():
    #def __init__(self, price, last_time):
    def __init__(self, last_price, date_str):
        #current_time = datetime.datetime.now()
        self.start_time = datetime.datetime.strptime(date_str +' 9:00', '%Y%m%d %H:%M')
        self.end_time = datetime.datetime.strptime(date_str +' 13:30', '%Y%m%d %H:%M')
        #self.last_time = last_time
        self.one_minute = datetime.timedelta(minutes=1)
        self.current_time = self.start_time - self.one_minute
        
        self.price = last_price
        self.volume = 0
        self.sum_volume = 0

    def get_current_time(self):
        return self.current_time

    def get_date_str(self):
        return self.current_time.strftime('%Y%m%d')

    #總之就是每筆資料丟進來，他會幫你整理成每分鐘的資料，並決定要不要寫入的函式
    def check(self,data):
        #取得資料時間
        time = datetime.datetime.strptime(str(self.current_time.date()) + ' ' + data['t'], '%Y-%m-%d %H:%M:%S')
        if time == self.end_time:
            time_end = 1
        else:
            time_end = 0

        #write_data決定要不要寫入這筆資料
        if time >= self.current_time + self.one_minute:
            #self.last_time = self.current_time
            self.current_time = self.current_time + self.one_minute
            write_data = 1
        else:
            write_data = 0
        
        #time_wrong代表資料往後跳了好幾分鐘，所以要一直寫入資料到這筆資料的時間
        if time >= self.current_time + self.one_minute:
            time_wrong = 1
        else:
            time_wrong = 0
        
        #取得這筆資料的價錢
        if data['z'] != '-':
            self.price = float(data['z'])

        #計算成交量
        if (write_data == 1) and (time_wrong == 0) and ('v' in data) and (data['v']!='-'):
            minute_volume = int(data['v']) - self.volume
            self.volume = int(data['v'])
            self.sum_volume = int(data['v'])
        else:
            minute_volume = 0

        #return write_data, time_wrong, self.price, minute_volume, self.last_time, self.current_time
        return write_data, time_wrong, time_end, {'price':self.price, 'volume':minute_volume, 'time':self.current_time, 'sum_volume':self.sum_volume}

'''
data = {"tv":"91","ps":"91","pz":"248.5000","bp":"0","fv":"4","oa":"247.5000","ob":"247.0000","a":"249.0000_249.5000_250.0000_250.5000_251.0000_","b":"248.0000_247.5000_247.0000_246.5000_246.0000_","c":"3665","d":"20210917","ch":"3665.tw","ot":"14:30:00","tlong":"1631860200000","io":"RR","f":"15_15_55_20_41_","ip":"0","g":"15_2_8_18_32_","mt":"000000","ov":"809","h":"250.0000","i":"31","it":"12","oz":"247.0000","l":"240.0000","n":"貿聯-KY","o":"241.5000","p":"0","ex":"tse","s":"91","t":"13:30:00","u":"264.0000","v":"1696","w":"216.0000","nf":"貿聯控股公司","y":"240.0000","z":"248.5000","ts":"0"}
price = 30
t = Timer(price)
write_data, time_wrong, ret = t.check(data)
print(write_data)
print(time_wrong)
print(ret)
'''
