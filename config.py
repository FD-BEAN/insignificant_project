from datetime import date


class Settings:
    def __init__(self):
        self.start_date = date.today()
        self.end_date = self.start_date
        self.rolling_size = 130  #half year
        self.rtn_horizon = 1  #daily 1, weekly 5...
        self.N = 10
        self.coef = 'corr_coef'


ticker_1 = '000001'
ticker_2 = '000002'
keyword = 'all_indices'
index_code = 399994