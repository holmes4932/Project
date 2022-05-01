#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import pandas as pd

class Technical_Calculator():
    def __init__(self, data, last_time, period):
        self.data = data
        self.last_time = last_time
        self.period = period
        
    def push(self, price, volume, time):
        
        self.cal_RSI(price, time)
        self.cal_KD(price, self.last_time, time)
        self.cal_MA(price, time)
        self.cal_MACD(price, self.last_time)
        self.cal_avg_price(price, volume, time)

        self.last_time = time
        
        self.data.loc[time] = [
            price,
            volume,
            self.RSI,
            self.K,
            self.D,
            self.MA5,
            self.MA10,
            self.MA20,
            self.MACD,
            self.OSC,
            self.DIF,
            self.EMA12,
            self.EMA26,
            self.avg_price
        ]

        #return self.data.loc[time]
        return self.data.tail(20), time
    
    def get_data(self):
        return self.data

    def get_last_data(self):
        time = self.last_time
        data = {
            'Current Price' : self.data.loc[time]['Current Price'],
            'Volume' : self.data.loc[time]['Volume'],         
            'RSI' : self.data.loc[time]['RSI'],           
            'K' : self.data.loc[time]['K'],                
            'D' : self.data.loc[time]['D'],                 
            'MA5' : self.data.loc[time]['MA5'],               
            'MA10' : self.data.loc[time]['MA10'],             
            'MA20' : self.data.loc[time]['MA20'],              
            'MACD' : self.data.loc[time]['MACD'],               
            'OSC' : self.data.loc[time]['OSC'],            
            'DIF' : self.data.loc[time]['DIF'],               
            'EMA12' : self.data.loc[time]['EMA12'],             
            'EMA26' : self.data.loc[time]['EMA26'],             
            'avg price' : self.data.loc[time]['avg price']
        }
        return data
        

    def cal_RSI(self, price, time):
        RSI_num = 14
        data = self.data['Current Price'].tail(RSI_num)
        data.loc[time] = price
        
        last_num = -1
        up = []
        down = []
        for num in data:
            if last_num != -1:
                dis = num - last_num
                if dis > 0:
                    up.append(dis)
                    down.append(0)
                elif dis < 0:
                    up.append(0)
                    down.append(dis * -1)
                else:
                    up.append(0)
                    down.append(0)
            last_num = num
                
        up_avg = sum(up) / RSI_num
        down_avg = sum(down) / RSI_num

        if (up_avg + down_avg) == 0:
            self.RSI = 0
        else:
            self.RSI = float(int(up_avg / (up_avg + down_avg)*1000))/10

    def cal_KD(self,price,last_time,time):
        KD_num = 9
        #取最後8筆資料
        data = self.data['Current Price'].tail(KD_num - 1)
        #新增最新價格到最後一個row
        data.loc[time] = price

        max = data.max()
        min = data.min()
        
        if max == min:
            RSV = 0
        else:
            RSV = ((price - min)*100)/(max - min)

        #取最後一筆資料
        last = self.data.loc[last_time]
        self.K = ((last['K'])*2 + (RSV))/3
        self.D = ((last['D'])*2 + (self.K))/3

    def cal_MA(self, price, time):
        MA5_data = self.data['Current Price'].tail(5 - 1)
        MA5_data.loc[time] = price
        MA10_data = self.data['Current Price'].tail(10 - 1)
        MA10_data.loc[time] = price
        MA20_data = self.data['Current Price'].tail(20 - 1)
        MA20_data.loc[time] = price

        self.MA5 = sum(MA5_data) / 5
        self.MA10 = sum(MA10_data) / 5
        self.MA20 = sum(MA20_data) / 5
        
    def cal_MACD(self, price, last_time):
        n = 12
        m = 26
        x = 9

        #取最後一筆資料
        last = self.data.loc[last_time]

        self.EMA12 = (last['EMA12'] * (n-1) + price * 2) / (n+1)
        self.EMA26 = (last['EMA26'] * (m-1) + price * 2) / (m+1)
        self.DIF = self.EMA12 - self.EMA26
        self.MACD = (last['MACD'] * (x-1) + self.DIF * 2) / (x+1)
        self.OSC = self.DIF - self.MACD

    def cal_avg_price(self, price, volume, time):#
        self.avg_price = 0
        first = datetime.datetime.strptime(str(time.date())+'9:00', '%Y-%m-%d%H:%M')
        
        freq_str = '{}min'.format(self.period)
        index = pd.date_range(start = first, end = time, freq = freq_str)
        
        sum_price = 0
        sum_volume = 0

        for i in index:
            if i != time:
                sum_price = sum_price + (self.data.loc[i]['Current Price'] * self.data.loc[i]['Volume'])
                sum_volume = sum_volume + self.data.loc[i]['Volume']
        
        sum_price = sum_price + (price * volume)
        sum_volume = sum_volume + volume

        if sum_volume == 0:
            self.avg_price = 0
        else:
            self.avg_price = sum_price / sum_volume



