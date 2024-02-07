import pandas as pd
import adata as ad_util
from sspipe import px, p


class StockSummaryWrapper:

    def __init__(self):
        self.data_dirs = {
            'all_stocks': r'C:\Github\data\stocks\all_stock_tickers.pkl',
            'all_concepts': r'C:\Github\data\stocks\all_concept_tickers.pkl',
            'all_constituents': r'C:\Github\data\stocks\all_INDEXPLACEHOLDER_member_tickers.pkl',
            'all_concepts_east': r'C:\Github\data\stocks\all_concept_tickers_east.pkl',
            'all_constituents_east': r'C:\Github\data\stocks\all_INDEXPLACEHOLDER_member_tickers_east.pkl',
            'all_indices': r'C:\Github\data\stocks\all_indices.pkl',
            'all_etf': r'C:\Github\data\stocks\all_etf.pkl',
            'all_cb': r'C:\Github\data\stocks\all_cb.pkl',
            'all_index_members': r'C:\Github\data\stocks\all_INDEXPLACEHOLDER_index_members.pkl'
        }

    def print_available_keywords(self):
        print(','.join(list(self.data_dirs.keys())))

    @staticmethod
    def execute_actions(keyword, index_code=None):
        if keyword == 'all_stocks':
            out = ad_util.stock.info.all_code()
        elif keyword == 'all_concepts':
            out = ad_util.stock.info.all_concept_code_ths()
        elif keyword == 'all_constituents':
            out = ad_util.stock.info.concept_constituent_ths(index_code=index_code)
        elif keyword == 'all_concepts_east':
            out = ad_util.stock.info.all_concept_code_east()
        elif keyword == 'all_constituents_east':
            out = ad_util.stock.info.concept_constituent_east(index_code=index_code)
        elif keyword == 'all_indices':
            out = ad_util.stock.info.all_index_code()
        elif keyword == 'all_index_members':
            out = ad_util.stock.info.index_constituent(index_code=index_code)
        elif keyword == 'all_etf':
            out = ad_util.fund.info.all_etf_exchange_traded_info()
        elif keyword == 'all_cb':
            out = ad_util.bond.info.all_convert_code()
        else:
            out = pd.DataFrame()
        return out

    def get_data(self, keyword, refresh=False, index_code=None, save_data=True):
        if keyword not in self.data_dirs.keys():
            raise Exception(f'Please use supported keywords: {self.data_dirs.keys()}!')
        save_dir = self.data_dirs.get(keyword)
        if keyword in ['all_constituents', 'all_constituents_east', 'all_index_members']:
            if index_code is None:
                raise Exception('index_code cannot be None for all_index_members keyword!')
            else:
                if save_dir is not None:
                    save_dir = save_dir.replace('INDEXPLACEHOLDER', index_code)
        if refresh:
            out = self.execute_actions(keyword, index_code)
        else:
            try:
                out = pd.read_pickle(save_dir)
            except (ValueError, FileNotFoundError, EOFError):
                out = self.execute_actions(keyword, index_code)
        if save_dir is not None and save_data:
            try:
                out.to_pickle(save_dir)
            except RecursionError:
                import sys
                sys.setrecursionlimit(10000)
                print('Second Try')
                out.to_pickle(save_dir)
        return out


ss_util = StockSummaryWrapper()


# The function below gives all stock data in the market
def prepare_rsh_data(index_list=None, keyword='all_index_members', frequency=1, refresh_uni=False,
                     refresh_rsh=False, rsh_data_dir=None):

    read_status = False
    out = pd.DataFrame()
    if rsh_data_dir is None:
        raise Exception('Target pickle dir cannot be None!')
    if not refresh_rsh:
        try:
            out = pd.read_pickle(rsh_data_dir)
            read_status = True
        except (ValueError, FileNotFoundError, EOFError):
            print('Cached data not found! Regenerating...')
            read_status = False

    if refresh_rsh or not read_status:
        all_universe = ss_util.get_data('all_stocks', refresh=refresh_uni)
        if index_list is None:
            raw_universe = all_universe.copy()
        else:
            sub_universe_list = []
            for idx in index_list:
                sub_universe_list.append(ss_util.get_data(keyword, index_code=idx, refresh=refresh_uni))
            raw_universe = pd.concat(sub_universe_list, axis=0, ignore_index=True)
        rsh_universe = raw_universe | \
                       px.merge(all_universe, on='stock_code', how='left') | \
                       px[~px.list_date.isna()] | \
                       px[~px.stock_code.str.startswith('9')] | \
                       px[~px.stock_code.str.startswith('2')] | \
                       px[~px.stock_code.str.startswith('3')] | \
                       px[~px.stock_code.str.startswith('68')] | \
                       px[['stock_code', 'list_date']]

        res_list = []
        universe_list = rsh_universe['stock_code'].tolist()
        cnt = 1
        total = len(universe_list)
        for ticker in universe_list:
            print(ticker, int(cnt/total*100), '%', end='\r')
            ticker_df = ad_util.stock.market.get_market(stock_code=ticker, k_type=frequency)
            res_list.append(ticker_df)
            cnt += 1
        out = pd.concat(res_list, axis=0, ignore_index=True)
        out.to_pickle(rsh_data_dir, compression='gzip')

    return out


# The function below gives price data of single stock
def simple_price_data(ticker='000001', frequency=1):
    return ad_util.stock.market.get_market(stock_code=ticker, k_type=frequency)
