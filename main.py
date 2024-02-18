import imp
fp, pathname, description = imp.find_module('utils')
utils = imp.load_module('utils', fp, pathname, description)
from utils import *

fp, pathname, description = imp.find_module('data_util')
data_util = imp.load_module('data_util', fp, pathname, description)
from data_util import *

fp, pathname, description = imp.find_module('config')
config = imp.load_module('config', fp, pathname, description)
from config import *

import numpy as np

data_ssutil = StockSummaryWrapper()
setting = Settings()

tik1 = ticker_1
tik2 = ticker_2
n_days = 260
end_date = date.today()
start_date = end_date - timedelta(days=n_days)

stock_df = get_universe_price_data('all_indices', 'all_index_members', '399020')
correl_df = get_universe_correlation(start_date, end_date, ticker_1=tik1, stock_df=stock_df)

hedge_basket = generate_weighted_hedge_basket(correl_df, trade_date=correl_df.sort_values(by='trade_date').trade_date.unique()[-1])


#
# from dash import Dash, dcc, html, Input, Output
# import plotly.graph_objects as go
#
# app = Dash(__name__)
#
#
# app.layout = html.Div([
#     html.H4('Interactive color selection with simple Dash example'),
#     html.P("Select color:"),
#     dcc.Dropdown(
#         id="dropdown",
#         options=['Gold', 'MediumTurquoise', 'LightGreen'],
#         value='Gold',
#         clearable=False,
#     ),
#     dcc.Graph(id="graph"),
# ])
#
#
# @app.callback(
#     Output("graph", "figure"),
#     Input("dropdown", "value"))
# def display_color(color):
#     fig = go.Figure(
#         data=go.Bar(y=[2, 3, 1], # replace with your own data source
#                     marker_color=color))
#     return fig
#
#
# app.run_server(debug=True)


