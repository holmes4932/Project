#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import datetime

from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dropout, Dense
from keras.callbacks import ModelCheckpoint
from plotly.graph_objs import Scatter, Layout
from plotly.offline import plot
from tkinter import _flatten

class LSTM_model():
    def __init__(self,stock_number,period,batch_size=100,epochs=15):
        
        self.num = stock_number
        self.batch_size = batch_size
        self.epochs = epochs
        self.period = period
        self.split_data = 0.8
        
        self.data = self.load_data(stock_number)
        r_counter,c_counter = self.data.shape

        price_label = self.data[['Current Price']]
        self.train_x, self.price_train_y, self.test_x, self.price_test_y = self.data_processing(self.data,price_label,sequence_length=10,split=self.split_data)
        self.price_model, self.price_model_path = self.build_model(c_counter,stock_number) #建立模型

    def load_data(self,stock_number):
        filename = '{}/{}-{}min.csv'.format('synthesis data', stock_number, self.period)
        data = pd.read_csv(filename, encoding= 'unicode_escape', index_col='Date & Time', parse_dates = {'Date & Time':[0,1]})
        parameter = [
            'Current Price',
            'Volume',
            'RSI',
            'K',
            'D',
            'MA5',
            'MA10',
            'MA20',
            'MACD',
            'OSC',
            'DIF',
            'EMA12',
            'EMA26',
            'avg price',
        ]
        for col in data.columns:
            if col not in parameter:
                data = data.drop(col,axis=1)
        return data

    def data_processing(self,train,price_label,sequence_length,split):
        #資料前處理 1.正規化 2.指定資料型態(float) 3.切割train(80%)資料與test(20%)資料

        self.scaler=MinMaxScaler() #建立標準化用的MinMaxScaler-縮小
        self.price_scalert=MinMaxScaler() #建立標準化用的MinMaxScaler物件-還原

        train_all=np.array(train).astype(float)
        train_all=self.scaler.fit_transform(train_all)

        price_label_all=np.array(price_label).astype(float)
        price_label_all=self.price_scalert.fit_transform(price_label_all)

        attrs = []
        price_labels = []

        for i in range(len(train_all)-sequence_length):
            #第1~10分鐘的所有參數作為attr
            attrs.append(train_all[i:i+sequence_length])
            #第11分鐘的價錢跟交易量作為label
            price_labels.append(price_label_all[i+sequence_length])

        x=np.array(attrs).astype('float64')
        price_y=np.array(price_labels).astype('float64')

        split_boundary=int(x.shape[0]*split)

        train_x = x[:split_boundary] #前80%的train attr
        test_x = x[split_boundary:] #後20%的test attr

        price_train_y = price_y[: split_boundary] #前80%的train label
        price_test_y = price_y[split_boundary:] #後20%的test label

        return train_x,price_train_y,test_x,price_test_y

    def build_model(self,c_counter,stock_number):
        folder = 'model'
        #date_str = datetime.datetime.today().strftime('%Y%m%d')
        model_path = '{}/{}-{}min.h5'.format(folder, stock_number, self.period)

        if not os.path.isdir(folder):
            os.mkdir(folder)
        
        if os.path.isfile(model_path):
            model = load_model(model_path)
        else:
            #建立模型
            model = Sequential()
            #第一層
            #units：隱藏層含128個神經元
            #input_shape：TIME_STEPS=10,INPUT_SIZE=行數
            model.add(LSTM(input_shape=(10,c_counter),units=128,return_sequences=True))
            #dropout1, 丟棄神經元比例 : 0.3
            model.add(Dropout(0.3))
            #第二層
            #units：隱藏層含128個神經元
            model.add(LSTM(units=128))
            #dropout2, 丟棄神經元比例 : 0.3
            model.add(Dropout(0.3))
            #第三層
            #DNN神經元個數 : 32
            #DNN激活函數 : ReLU
            model.add(Dense(units=32, activation='relu')) 
            #第四層
            #DNN神經元個數 : 1
            #DNN激活函數 : linear
            model.add(Dense(units=1, activation='linear')) 
            #梯度下降法 : Adam
            #損失函數 : MSE
            model.compile(loss="mse",optimizer="adam",metrics=['accuracy'])

        return model,model_path

    def training(self):
        #train model
        checkpoint = ModelCheckpoint(self.price_model_path, monitor='loss', verbose=1, save_best_only=True, mode='min')
        callbacks_list = [checkpoint]

        self.price_model.fit(
            self.train_x,
            self.price_train_y,
            batch_size=self.batch_size,
            epochs=self.epochs,
            #validation_split=0.1,
            validation_data=(self.test_x,self.price_test_y), 
            callbacks=callbacks_list
        )
        self.price_model.save(self.price_model_path)

    def fast_testing_score(self):
        #預測
        price_predict = self.price_model.predict(self.test_x)
        #轉換為1維矩陣
        price_predict_y = np.reshape(price_predict,(price_predict.size, ))
        price_predict_y = self.price_scalert.inverse_transform([[i] for i in price_predict_y]) #還原
        price_test_y= self.price_scalert.inverse_transform(self.price_test_y) #還原

        data = []
        result = []
        for original,predict in zip(price_test_y,price_predict_y):
            if len(data) == 10:
                correct = self.correction(data, predict[0])
                result.append({'original':original[0],'predict':predict[0],'correct':correct})
                data.pop(0)
            
            data.append({'original':original[0],'predict':predict[0]})

        testing_result_folder = 'testing result'
        if not os.path.isdir(testing_result_folder):
            os.mkdir(testing_result_folder)

        fieldnames = ['original', 'predict', 'correct']
        testing_result_path = '{}/{}-{}min-result.csv'.format(testing_result_folder,self.num,self.period)
        write_csv_file(testing_result_path, fieldnames, result)

    def slow_testing_score(self):
        row_num, col_num = self.data.shape
        split_boundary = row_num - int(row_num * self.split_data)
        testing_data = self.data.tail(split_boundary).copy()

        predict_window = 20

        result = []
        row, col = testing_data.shape
        while row > predict_window:
            #取得前20筆資料並預測
            testcase = testing_data.head(predict_window)
            predict,correct = self.predict_and_correction(testcase)

            #取得第21筆資料的index
            index = testing_data.head(predict_window + 1).index
            time = index[predict_window].strftime('%Y-%m-%d %H:%M')
            print(time)
            result.append({'時間' : time, '實際價錢' : testing_data.loc[time]['Current Price'], '預測價錢' : predict, '校正價錢' : correct})

            #刪掉第1筆資料
            row = row - 1
            testing_data = testing_data.tail(row)
        
        testing_result_folder = 'testing result'
        if not os.path.isdir(testing_result_folder):
            os.mkdir(testing_result_folder)

        fieldnames = ['時間', '實際價錢', '預測價錢', '校正價錢']
        testing_result_path = '{}/{}-{}min-result.csv'.format(testing_result_folder,self.num,self.period)
        write_csv_file(testing_result_path, fieldnames, result)

    def predict_and_correction(self,data):
        #傳入20筆資料
        predict_row = 10
        correction_row = 10

        row = predict_row + correction_row

        #拿前10筆來預測11~20筆
        testing_data = data.copy()
        predict_data = []
        for i in range(0,correction_row):
            #取得前10筆資料並預測
            testcase = testing_data.head(predict_row)
            predict = self.predict(testcase)

            #取得第11筆資料的index
            index = testing_data.head(predict_row + 1).index
            time = index[predict_row].strftime('%Y-%m-%d %H:%M')
            predict_data.append({'original' : testing_data.loc[time]['Current Price'], 'predict' : predict})

            #刪掉第1筆資料
            row = row - 1
            testing_data = testing_data.tail(row)

        #拿11~20筆資料預測第21筆
        predict = self.predict(data.tail(predict_row))
        correct = self.correction(predict_data, predict)

        return predict,correct


    def predict(self, data):
        np_data = np.array(data).astype(float)
        np_standard_data = self.scaler.transform(np_data)

        np_arr = [np_standard_data]
        np_arr = np.array(np_arr).astype('float64')
        
        price_predict = self.price_model.predict(np_arr)
        price_predict = self.price_scalert.inverse_transform(price_predict) #還原

        return price_predict[0][0]

    def correction(self, data, predict):
        #校正
        n=10
        #n:資料筆數
        rate=0.001
        sum=0

        for (index, value) in enumerate(data):
            Rt = value['original']
            Pt = value['predict']
            Bt =  Rt - Pt

            sum += abs(Bt)

            if index == n-1:
                C = sum/n
                if C > Rt*rate:
                    if Bt > 0:
                        return predict + C
                    elif Bt == 0:
                        return predict
                    elif Bt < 0:
                        return predict - C
                else:
                    return predict



class Time_calculator():
    def __init__(self,time):
        self.time = time
        self.one_minute = datetime.timedelta(minutes=1)
        self.one_day = datetime.timedelta(days=1)

    def next(self):
        time = self.time + self.one_minute
        if time > datetime.datetime.strptime(str(time.date())+' 13:30', '%Y-%m-%d %H:%M'):
            time = datetime.datetime.strptime(str(time.date() + self.one_day)+' 9:00', '%Y-%m-%d %H:%M')
            weekday = time.weekday() + 1
            while weekday > 5:
                time = datetime.datetime.strptime(str(time.date() + self.one_day)+' 9:00', '%Y-%m-%d %H:%M')
                weekday = time.weekday() + 1
        self.time = time
        return time

def write_csv_file(target_file, fieldnames, data):
    with open(target_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        for row in data:
            writer.writerow(row)
        
