import csv
import datetime
import os
import pandas as pd

def make_dir(target_folder):
    if not os.path.isdir(target_folder):
        os.mkdir(target_folder)

def write_csv_file(target_file, fieldnames, data):
    with open(target_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        for row in data:
            writer.writerow(row)

def read_csv_file(target_file):
    array = {}
    with open(target_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['時間'] != '':
                if isinstance(row['時間'],str):
                    #print('str')
                    pass
                else:
                    #print('time')
                    pass
                time = datetime.datetime.strptime(row['時間'], '%Y-%m-%d %H:%M')
                array[time] = row
    return array

class Time_calculator():
    def __init__(self,date_str,period):
        self.normal_time = datetime.datetime.strptime(str(date_str)+' 9:00', '%Y%m%d %H:%M')
        self.end_time = datetime.datetime.strptime(str(date_str)+' 13:29', '%Y%m%d %H:%M')
        self.counter = 0
        self.one_minute = datetime.timedelta(minutes=1)
        self.one_day = datetime.timedelta(days=1)
        self.period = period
        self.period_time = {}
        self.time = {}
        self.time_str = {}
        for minutes in self.period:
            self.period_time[str(minutes)] = self.one_minute * minutes
            self.time[str(minutes)] = self.normal_time + self.period_time[str(minutes)]
            #self.time[str(minutes)] = self.normal_time
            self.time_str[str(minutes)] = datetime.datetime.strftime(self.time[str(minutes)],'%Y-%m-%d %H:%M')

    def get_time_index(self):
        return self.time_str, datetime.datetime.strftime(self.normal_time,'%Y-%m-%d %H:%M')

    def next_minute(self):
        self.normal_time = self.normal_time + self.one_minute
        self.counter = self.counter + 1
        for minutes in self.period:
            if self.counter % minutes == 0:
                time = self.time[str(minutes)] + self.period_time[str(minutes)]
                if time > datetime.datetime.strptime(str(time.date())+' 13:29', '%Y-%m-%d %H:%M'):
                    time = datetime.datetime.strptime(str(time.date() + self.one_day)+' 9:00', '%Y-%m-%d %H:%M')
                    weekday = time.weekday() + 1
                    while weekday > 5:
                        time = datetime.datetime.strptime(str(time.date() + self.one_day)+' 9:00', '%Y-%m-%d %H:%M')
                        weekday = time.weekday() + 1
                self.time[str(minutes)] = time
                self.time_str[str(minutes)] = datetime.datetime.strftime(self.time[str(minutes)],'%Y-%m-%d %H:%M')
        return self.time_str, datetime.datetime.strftime(self.normal_time,'%Y-%m-%d %H:%M')

    def end(self):
        if self.normal_time > self.end_time:
            return 1
        else:
            return 0

def dump(days, stocks, period, technical_parameter):

    original_folder = 'testing result'
    extra_folder = 'synthesis data'
    target_folder = 'predict data'
    make_dir(target_folder)
    
    data = {}
    for stock in stocks:
        #讀取技術指標
        filename = '{}/{}-1min.csv'.format(extra_folder,stock)
        technical_data = pd.read_csv(filename, encoding= 'unicode_escape', index_col='Date & Time', parse_dates = {'Date & Time':[0,1]})

        #讀取model的預測結果
        for minutes in period:
            filename = '{}/{}-{}min-result.csv'.format(original_folder,stock,minutes)
            data[str(minutes)] = read_csv_file(filename)
        
        for date_str in days:
            Time = Time_calculator(date_str, period)
            time_index, normal_time = Time.get_time_index()

            output_data = []
            while not Time.end():
                minute_data = {}
                minute_data['time'] = normal_time
                for minutes in time_index:
                    minute_title = '{} min'.format(str(minutes))
                    minute_data_time = '{} min time'.format(str(minutes))
                    
                    tmp = datetime.datetime.strptime(time_index[str(minutes)],'%Y-%m-%d %H:%M')
                    #tmp2 = tmp.strftime('%Y/%m/%d %H:%M')
                    
                    #實際價錢以1分鐘為主
                    if minutes == '1':
                        minute_data['original'] = data[str(minutes)][tmp]['實際價錢'] 
                        for tec in technical_parameter:
                            minute_data[tec] = technical_data.loc[tmp][tec]
                    
                    print(minutes)
                    print(stock)
                    print(type(tmp))
                    minute_data[minute_title] = data[str(minutes)][tmp]['校正價錢'] 
                    minute_data[minute_data_time] = time_index[str(minutes)]
                    #print(minute_data)

                

                output_data.append(minute_data)
                time_index, normal_time = Time.next_minute()

            fieldnames = ['time','original']
            for minutes in period:
                fieldnames.append(str(minutes) + ' min')
                #fieldnames.append(str(minutes) + ' min time')

            for tec in technical_parameter:
                fieldnames.append(tec)

            target_file = '{}/{}-{}.csv'.format(target_folder, stock, date_str)
            write_csv_file(target_file, fieldnames, output_data)

days = ['20210818']
#days = ['20210816','20210817','20210818','20210819','20210820']
#days = ['20210823','20210824','20210825','20210826','20210827']
#days = ['20210830','20210831','20210901','20210902','20210903']
#days = ['20210906','20210907','20210908','20210909','20210910']
#days = ['20210913','20210914','20210915','20210916','20210917']
#days = ['20210922','20210923','20210924']
#days = ['20210927','20210928','20210929']
#days = ['20211001'] #3665沒有這天 股市休市 其他股票有這天
#days = ['20211004']
#stocks = ['2603','2609','2615'] #航運三雄
#stocks = ['00637L','3665','2330','2454'] #原始那四隻
#stocks = ['2603','2609','2615','00637L','3665','2330','2454']
stocks = ['00637L','2330']
period = [1,5,10]
technical_parameter = ['Volume', 'MA5', 'avg price']

dump(days, stocks, period, technical_parameter)
