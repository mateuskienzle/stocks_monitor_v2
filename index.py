from dash import html, dcc, no_update, callback_context
import dash
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import yfinance as yf
from tvDatafeed import TvDatafeed, Interval

from app import *
from components import home, header, wallet, row1


# Funções =======================================
def iterar_sobre_df_book(df_book_var: pd.DataFrame, ativos_org_var={}) -> dict:
    for _, row in df_book_var.iterrows():
        if not any(row['ativo'] in sublist for sublist in ativos_org_var):  
            ativos_org_var[row["ativo"]] = row['exchange']
    
    ativos_org_var['BVSPX'] = 'VANTAGE'
    return ativos_org_var 

def atualizar_historical_data(df_historical_var: pd.DataFrame, ativos_org_var={}) -> pd.DataFrame:
    tv = TvDatafeed()
    for symb_dict in ativos_org_var.items():
        new_line = tv.get_hist(*symb_dict, n_bars=5000)[['symbol','close']].reset_index()
        df_historical_var = pd.concat([df_historical_var, new_line], ignore_index=True)

    return df_historical_var.drop_duplicates(ignore_index=True)
    
# Checando se o book de transações existe
ativos_org = {}
try:    # caso exista, ler infos
    df_book = pd.read_csv('book_data.csv', index_col=0)
    ativos_org = iterar_sobre_df_book(df_book)
except: # caso não exista, criar df
    df_book = pd.DataFrame(columns=['date', 'preco', 'tipo', 'ativo', 'exchange', 'vol', 'valor_total'])


try:
    df_historical_data = pd.read_csv('historical_data.csv', index_col=0)
except:
    columns = ['datetime', 'symbol', 'close']
    df_historical_data = pd.DataFrame(columns=columns)

df_historical_data = atualizar_historical_data(df_historical_data, ativos_org)

df_book = df_book.to_dict() 
df_historical_data = df_historical_data.to_dict()

# toast = dbc.Toast("Seu ativo foi cadastrado com sucesso!",
#                             id="positioned_toast",
#                             header="Confirmação de cadastro",
#                             is_open=False,
#                             dismissable=False,
#                             duration = "4000",
#                             icon="success",
#                             style={"position": "fixed", "top": 66, "right": 10, "width": 350})

app.layout = dbc.Container([
    dcc.Location(id="url"),
    dcc.Store(id='book_data_store', data=df_book, storage_type='memory'),
    dcc.Store(id='historical_data_store', data=df_historical_data, storage_type='memory'),
    dcc.Store(id='layout_data', data=[], storage_type='memory'),
    # dcc.Interval(id='interval_update', interval=1000*600),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    header.layout
                ], className= 'header_layout'),
            ]),
            dbc.Row([
                dbc.Col([
                   row1.layout
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                    # toast
                ]),
            ],id="page-content"),
        ])
    ])

], fluid=True)


@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
)

def render_page(pathname):
    if pathname == '/home' or pathname == '/':
        return home.layout
    if pathname == '/wallet':
        return wallet.layout
    # else:
    #     return dbc.Container([
    #         html.H1("404: Not found")
    #     ])


# Callback para atualizar as databases
@app.callback(
    Output('historical_data_store', 'data'),
    # Input('interval_update', 'n_intervals'),
    Input('book_data_store', 'data'),
    State('historical_data_store', 'data')
)
def atualizar_databases(book_data, historical_data):
    df_book = pd.DataFrame(book_data)
    df_historical = pd.DataFrame(historical_data)

    ativos = iterar_sobre_df_book(df_book)
    # import pdb; pdb.set_trace()
    df_historical = atualizar_historical_data(df_historical, ativos)

    # atualizando os CSV's
    # df_book.to_csv('book_data.csv')
    df_historical.to_csv('historical_data.csv')

    return df_historical.to_dict()


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)