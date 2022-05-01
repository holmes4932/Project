#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import time
import random
import threading

from data_crawler import *
from stock import *
from GUI import *

class Program_Manager():
    def __init__(self, state = '', testing_date_str = '', period = [1,5,10], stock_filename = 'stocknumber.xlsx', close_filename = 'close.xlsx'):
        self.stocknumbers, self.stockmoney = self.read_stock(stock_filename)
        self.close_date = self.read_close(close_filename)
        self.period = period     

        #判斷是正式還是測試來取得日期
        if state == '': #正式
            self.get_open_time()
        else: #測試
            self.today_date_str = testing_date_str

        #建立股票物件
        self.stock_data = {}
        for stock,money in zip(self.stocknumbers, self.stockmoney):
            self.stock_data[stock] = Stock(stock, self.period, self.today_date_str, money['money'])

        gui = threading.Thread(target = self.GUI_thread, args = (self.stocknumbers, self.stock_data))
        
        if state == '': #正式
            self.crawler = Data_Crawler()
            gui.start()
            self.run()
        else: #test
            filename = 'data/{}/All_data.xlsx'.format(testing_date_str)
            self.testing_data = {}
            for stock in self.stocknumbers:
                self.testing_data[stock] = self.read_excel_file(filename, stock)
            gui.start()
            self.testing()
        gui.join()
                
    def run(self):
        time_end = {}
        for stock in self.stocknumbers:
            time_end[stock] = 0

        current_time = datetime.datetime.now()
        while current_time < self.start_time:
            time.sleep(5)
            current_time = datetime.datetime.now()

        while self.check_end(time_end) == 0:
            current_time = datetime.datetime.now()
            print('current time is :',current_time)
            data = self.crawler.get_data()
            for row in data:
                time_end[row['c']] = self.stock_data[row['c']].push(row) 
            time.sleep(random.randint(3,7))

    def testing(self):
        #initial
        time_end = {}
        for stock in self.stocknumbers:
            time_end[stock] = 0

        #run
        for i in range(1,1000):
            for stock in self.stocknumbers:
                if i < len(self.testing_data[stock]) and time_end[stock] == 0:
                    time_end[stock] = self.stock_data[stock].push(self.testing_data[stock][i])
            time.sleep(1)
    
    def GUI_thread(self, stocknumbers, stock_data):
        self.gui = GUI(stocknumbers, stock_data)

    def check_end(self, time_end):
        for stock in time_end:
            if time_end[stock] == 0:
                return 0
        return 1

    #取得今天開盤時間跟關盤時間
    def get_open_time(self):
        current_time = datetime.datetime.now()
        self.today_date_str = current_time.strftime('%Y%m%d')
        self.today_date = current_time.date()
        self.start_time = datetime.datetime.strptime(str(current_time.date())+'9:00', '%Y-%m-%d%H:%M')
        self.end_time = datetime.datetime.strptime(str(current_time.date())+'13:31', '%Y-%m-%d%H:%M')
        weekday = current_time.weekday() + 1
        
        if weekday > 5:
            print('今天是假日喔，沒開盤')
            exit(0)
        elif self.today_date_str in self.close_date:
            print('今天是特別休假日，沒開盤')
            exit(0)
        elif current_time > self.end_time:
            print('今天已經結束囉')
            exit(0)
        
    #讀取為開盤日檔案
    def read_close(self, file):
        workbook = openpyxl.load_workbook(file)
        sheets = workbook.sheetnames
        booksheet = workbook[sheets[0]] 
        rows = booksheet.rows

        array = []
        for row in rows:
            line=[col.value for col in row]
            array.append(str(line[0]))
        return array

    #讀取股票和本金檔案
    def read_stock(self, file):
        workbook = openpyxl.load_workbook(file)
        sheets = workbook.sheetnames
        booksheet = workbook[sheets[0]] 
        rows = booksheet.rows

        stocks = []
        stocks_money = []
        for row in rows:
            line=[col.value for col in row]
            stocks.append(str(line[0]))
            stocks_money.append({'stock': str(line[0]), 'money': int(line[1])})
        return stocks, stocks_money

    #讀取all_data測試資料
    def read_excel_file(self,original,sheet):
        workbook = openpyxl.load_workbook(original)

        booksheet = workbook[sheet] 
        rows = booksheet.rows
        array = []
        ref = []
        
        for row in rows:
            line = [col.value for col in row]
            if len(line)!=0 and line[0]!='資料時間' and line[0]!='tv' and line[0] is not None:
                line[0]=str(line[0])
                tmp = {i : j for i,j in zip(ref,line)}
                array.append(tmp)
            else:
                ref = line
        return array

#Program_Manager('testing', '20211115')
Program_Manager()
