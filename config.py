import data_util
import datetime

ss_util = data_util.StockSummaryWrapper()

class Settings:
    def __init__(self):
        self.start_date = datetime.date.today()
        self.end_date = self.start_date
        self.rolling_size = 130 #half year
        self.rtn_horizon = 1 #daily 1, weekly 5...


ticker_1 = '000001'
ticker_2 = '000002'

