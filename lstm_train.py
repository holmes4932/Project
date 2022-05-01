from lstm import *

period = [1]
for minutes in period:
    obj = LSTM_model('2330', period = minutes, epochs = 10, batch_size = 32)
    obj.training()

