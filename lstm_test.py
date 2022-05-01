from lstm import *

period = [1]
for minutes in period:
    obj = LSTM_model('00637L', minutes)
    #obj.slow_testing_score()
    obj.fast_testing_score()