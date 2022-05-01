#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import time
import random
import openpyxl
import requests

class Data_Crawler():
    def __init__(self, stock_filename = 'stocknumber.xlsx'):
        self.stocks = self.file_to_array(stock_filename)
        #self.close_date = self.file_to_array(close_filename)
        self.get_url(self.stocks)

    #讀取目標股票轉成陣列回傳
    def file_to_array(self, file):
        workbook = openpyxl.load_workbook(file)
        sheets = workbook.sheetnames
        booksheet = workbook[sheets[0]] 
        rows = booksheet.rows

        array = []
        for row in rows:
            line=[col.value for col in row]
            array.append(str(line[0]))
        return array

    #將目標陣列轉換成網址
    def get_url(self, stocks):
        endpoint = 'http://mis.twse.com.tw/stock/api/getStockInfo.jsp'
        # Add 1000 seconds for prevent time inaccuracy
        timestamp = int(time.time() * 1000 + 1000000)
        channels = '|'.join('tse_{}.tw'.format(target) for target in stocks)
        self.query_url = '{}?_={}&ex_ch={}'.format(endpoint, timestamp, channels)

    #抓資料
    def get_data(self):
        failed_cnt = 0
        data = []
        while data == []:
            failed_cnt = failed_cnt + 1
            try:
                # Get original page to get session
                req = requests.session()
                req.get('http://mis.twse.com.tw/stock/index.jsp', headers={'Accept-Language': 'zh-TW'})
                response = req.get(self.query_url)
                content = json.loads(response.text)
            except Exception as err:
                print(err)
                time.sleep(random.randint(3,7))
            else:
                data = content['msgArray']
        return data


'''
[
    {"tv":"91","ps":"91","pz":"248.5000","bp":"0","fv":"4","oa":"247.5000","ob":"247.0000","a":"249.0000_249.5000_250.0000_250.5000_251.0000_","b":"248.0000_247.5000_247.0000_246.5000_246.0000_","c":"3665","d":"20210917","ch":"3665.tw","ot":"14:30:00","tlong":"1631860200000","io":"RR","f":"15_15_55_20_41_","ip":"0","g":"15_2_8_18_32_","mt":"000000","ov":"809","h":"250.0000","i":"31","it":"12","oz":"247.0000","l":"240.0000","n":"貿聯-KY","o":"241.5000","p":"0","ex":"tse","s":"91","t":"13:30:00","u":"264.0000","v":"1696","w":"216.0000","nf":"貿聯控股公司","y":"240.0000","z":"248.5000","ts":"0"},
    {"tv":"22082","ps":"22082","pz":"600.0000","bp":"0","fv":"57","oa":"606.0000","ob":"605.0000","a":"601.0000_602.0000_603.0000_605.0000_606.0000_","b":"600.0000_599.0000_598.0000_597.0000_596.0000_","c":"2330","d":"20210917","ch":"2330.tw","ot":"14:30:00","tlong":"1631860200000","f":"3_7_79_3_31_","ip":"0","g":"1107_846_655_855_304_","mt":"000000","ov":"36715","h":"610.0000","i":"24","it":"12","oz":"606.0000","l":"599.0000","n":"台積電","o":"600.0000","p":"0","ex":"tse","s":"22082","t":"13:30:00","u":"660.0000","v":"40624","w":"540.0000","nf":"台灣積體電路製造股份有限公司","y":"600.0000","z":"600.0000","ts":"0"},
    {"tv":"552","ps":"551","nu":"http://www.yuantaetfs.com/#/RtNav/Index","pz":"20.5800","bp":"0","fv":"19","oa":"20.8000","ob":"20.6800","a":"20.5900_20.6000_20.6100_20.6200_20.6300_","b":"20.5800_20.5700_20.5600_20.5500_20.5400_","c":"00637L","d":"20210917","ch":"00637L.tw","ot":"14:30:00","tlong":"1631860200000","f":"32_41_17_992_930_","ip":"0","g":"406_751_955_1299_1435_","mt":"000000","ov":"457","h":"20.6900","it":"02","oz":"20.6800","l":"19.9500","n":"元大滬深300正2","o":"20.1800","p":"0","ex":"tse","s":"552","t":"13:30:00","u":"9999.9500","v":"44894","nf":"元大滬深300傘型證券投資信託基金之滬深300單日正向2倍證券投資信託基金","y":"20.2600","z":"20.5800","ts":"0"},
    {"tv":"1743","ps":"1742","pz":"940.0000","bp":"0","fv":"7","oa":"941.0000","ob":"940.0000","a":"942.0000_943.0000_944.0000_945.0000_946.0000_","b":"940.0000_939.0000_938.0000_937.0000_936.0000_","c":"2454","d":"20210917","ch":"2454.tw","ot":"14:30:00","tlong":"1631860200000","f":"2_2_5_13_12_","ip":"0","g":"109_60_67_274_58_","mt":"000000","ov":"8343","h":"952.0000","i":"24","it":"12","oz":"940.0000","l":"936.0000","n":"聯發科","o":"940.0000","p":"0","ex":"tse","s":"1743","t":"13:30:00","u":"1025.0000","v":"7207","w":"843.0000","nf":"聯發科技股份有限公司","y":"936.0000","z":"940.0000","ts":"0"}
]
'''