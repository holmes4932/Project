原始資料：data/ 
(請勿將1/6的資料刪除)
==============================================================
前置作業：

python synthesis.py
data/ -> synthesis data/
將資料算出技術指標後合併到同一個檔案
可以自行在period 中設定要以幾分鐘為單位

==============================================================
LSTM：

python lstm_train.py
synthesis data/ -> model/
用LSTM來訓練模型
訓練好的模型匯存到model之中
要是中途斷掉的話可以再執行一次
雖然看起來epoch會從頭開始跑
但會儲存上次的狀態
epoch跟batch size跟分鐘數可以自行在lstm_training.py自行更改

python lstm_test.py
model/ + synthesis data/ -> testing result/
使用訓練好的model來預測股價
並且將結果存到testing result中

==============================================================
策略整理：

python bigger.py
testing result/ -> predict data/
將LSTM測試完的資料整理成每分鐘導向的格式
以日期為主整理成一個檔案
要彙整的股票跟日期可以自行從主程式中丟進dump()

==============================================================
每日邊抓資料邊預測：

python program_manager.py
synthesis data/ & model/ -> data/ & minute predict/ & final result/
要改股票跟價錢的話要到stocknumber.xlsx改

==============================================================
每日測試：

python program_manager.py
data/[date]/All_data.xlsx & synthesis data/ & model/ -> data/ & minute predict/ & final result/
只要將program_manager.py最下面宣告的地方加入testing參數跟日期就能測試
把All_data.xlsx的資料當成每天抓的資料餵給程式

