import config as cfg
import data_util
import warnings
from sspipe import px
import pandas as pd
from statsmodels.regression.rolling import RollingOLS
from concurrent.futures import ThreadPoolExecutor

setting = cfg.Settings()
data_ssutil = data_util.StockSummaryWrapper()


def get_correl(start_date=setting.start_date, end_date=setting.end_date, rolling_size=setting.rolling_size,
               rtn_horizon=setting.rtn_horizon, ticker_1=cfg.ticker_1, ticker_2=cfg.ticker_2):
    df_ticker1 = data_util.simple_price_data(ticker_1, rtn_horizon)[['trade_date', 'stock_code', 'close']].dropna()
    df_ticker2 = data_util.simple_price_data(ticker_2, rtn_horizon)[['trade_date', 'stock_code', 'close']].dropna()

    # Merger two price data
    combined_df = df_ticker1 | \
                  px.merge(df_ticker2, on='trade_date', how='inner')

    combined_df.close_x = combined_df.close_x.astype(float)
    combined_df.close_y = combined_df.close_y.astype(float)

    combined_df.trade_date = pd.to_datetime(combined_df.trade_date).dt.date
    combined_df = combined_df.loc[(combined_df.trade_date > start_date) & (combined_df.trade_date <= end_date)]

    corr_df = combined_df.close_x.rolling(rolling_size).corr(combined_df.close_y)
    rols = RollingOLS(combined_df.close_x, combined_df.close_y, window=rolling_size)
    rres = rols.fit()
    reg_df = rres.params.copy()

    result_df = reg_df.copy() | \
                px.set_axis(['reg_coef'], axis='columns') | \
                px.assign(corr_coef=corr_df,
                          trade_date=combined_df.trade_date,
                          ticker_1=ticker_1,
                          ticker_2=ticker_2) | \
                px.reset_index(drop=True) | \
                px.dropna()
    # print(result_df)

    return result_df


def get_index_code(keyword):
    if keyword == 'all_concepts':
        classification = 'all_constituents'
    elif keyword == 'all_concepts_east':
        classification = 'all_constituents_east'
    elif keyword == 'all_indices':
        classification = 'all_index_members'
    warnings.warn(
        'Missing index keyword and index code. Use index keyword ' + classification + ' and select index code from below table to try again')
    print(data_ssutil.execute_actions(keyword))


def get_universe_price_data(keyword, index_keyword=None, index_code=None, rtn_horizon=setting.rtn_horizon):
    stock_list = None
    if keyword in ['all_concepts', 'all_concepts_east', 'all_indices']:
        if index_keyword is None or index_code is None:
            get_index_code(keyword)
            return
        else:
            stock_list = data_ssutil.execute_actions(index_keyword, str(index_code))
            if stock_list is None or stock_list.empty:
                raise Exception('Stock list of ' + index_keyword + ' ' + str(index_code) + ' is none or empty.')
    else:
        stock_list = data_ssutil.execute_actions(keyword)
        if stock_list is None or stock_list.empty:
            raise Exception('Stock list of ' + index_keyword + ' ' + str(index_code) + ' is none or empty.')

    # stock_px_df = pd.DataFrame()
    #
    # for stock_code in stock_list.stock_code:
    #     if stock_px_df.empty == True:
    #         stock_px_df = simple_price_data(str(stock_code), rtn_horizon).copy()
    #     else:
    #         stock_px_df = pd.concat([stock_px_df, simple_price_data(str(stock_code), rtn_horizon).copy()])
    return stock_list


def get_universe_correlation(start_date=setting.start_date, end_date=setting.end_date,
                             rolling_size=setting.rolling_size,
                             rtn_horizon=setting.rtn_horizon, ticker_1=cfg.ticker_1, stock_df=None):
    if stock_df is None or stock_df.empty:
        raise Exception('Stock list is none or empty.')

    stock_list = stock_df.stock_code.unique().tolist()

    with ThreadPoolExecutor() as excutor:
        correl_list = list(excutor.map(lambda x: get_correl(*x),
                                       [(start_date, end_date, rolling_size, rtn_horizon, ticker_1, stock)
                                        for stock in stock_list]))
    # correl_list = []
    # for stock in stock_list:
    #     # print(stock)
    #     correl_list.append(get_correl(start_date, end_date, rolling_size,
    #                                   rtn_horizon, ticker_1, stock))
    # todo add exception handling when no pair correl

    correl_df = pd.concat(correl_list, axis=0, ignore_index=True)

    return correl_df


def generate_weighted_hedge_basket(correl_df=None, N=setting.N, trade_date=setting.end_date, coef=setting.coef):
    if correl_df is None or correl_df.empty:
        warnings.warn('Stock pair correlation is none or empty.')
        return

    top_tickers = correl_df.loc[correl_df.trade_date == trade_date].sort_values(by=[coef], ascending=False).head(N)
    top_tickers['hedge_ratio'] = top_tickers[coef] / top_tickers[coef].abs().sum()

    return top_tickers[['trade_date', 'ticker_2', 'hedge_ratio']].reset_index(drop=True)

# def plot_coef(correl_df=None, )
