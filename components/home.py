from dash import html, dcc, Input, Output, State, no_update
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from pandas.tseries.offsets import DateOffset
from datetime import date

from app import *


offsets = [DateOffset(days=5), DateOffset(months=1), DateOffset(months=3), DateOffset(months=6), DateOffset(years=1), DateOffset(years=2)] 
delta_titles = ['5 dias', '1 mês', '3 meses', '6 meses', '1 ano', '2 anos', 'Ano até agora']
PERIOD_OPTIONS = ['5d','1mo','3mo','6mo','1y','2y', 'ytd']

TIMEDELTAS = {x: y for x, y in zip(PERIOD_OPTIONS, offsets)}
TITLES = {x: y for x, y in zip(PERIOD_OPTIONS, delta_titles)}


#menu radar graph
INDICADORES = 'white'
BACKGROUND_RADAR = '#670067'  
LINHA_X = '#c1496b'
LINHA_Y = '#c1496b'
LINHAS_CIRCULARES = 'white'
LINHA_CIRCULAR_EXTERNA = 'white'
LINHAS_PREENCHIMENTO_1 = '#2d1106'
LINHAS_PREENCHIMENTO_2 = 'rgba(255,255,255,0.1)'
CAIXA_LEGENDA = 'rgba(0,0,0,0)'
VALORES_EIXO_X = 'white'
TAMANHO_INDICADORES = 15
TAMANHO_RADAR = 200

#menu line graph
AXIS_FONT_SIZE = 20
AXIS_COLOR = 'white'
LINHAS_DE_GRADE = 'rgba(255,255,255,0.1)'
LINHA_ZERO_X = 'rgba(255,255,255,0.2)'
LINHA_EVOLUCAO_PATRIMONIAL = '#670067'
LISTA_DE_CORES_LINHAS = ['#670067', '#9400d3', '#766ec5', '#120a8f', '#ff00cd', '#f34336', '#2d1106', '#00aaff', 'white']



HEIGHT={'height': '100%'}
MAIN_CONFIG = {
    "hovermode": "x unified",
    "legend": {"yanchor":"top", 
                "y":1.0, 
                "xanchor":"left",
                "x":0.8,
                "title": {"text": None},
                "bgcolor": CAIXA_LEGENDA},
    "margin": {"l":0, "r":0, "t":10, "b":0},
}
MAIN_CONFIG_2 = {
    "hovermode": "x unified",
    # "legend": {"yanchor":"top", 
    #             "y":1.0, 
    #             "xanchor":"left",
    #             "x":0.8,
    #             "title": {"text": None},
    #             "bgcolor": CAIXA_LEGENDA},
    "margin": {"l":0, "r":0, "t":10, "b":0},
}





df_ibov = pd.read_csv('tabela_ibov.csv')

df_ibov['Part. (%)'] = pd.to_numeric(df_ibov['Part. (%)'].str.replace(',','.'))
df_ibov['Qtde. Teórica'] = pd.to_numeric(df_ibov['Qtde. Teórica'].str.replace('.', ''))
df_ibov['Participação'] = df_ibov['Qtde. Teórica'] / df_ibov['Qtde. Teórica'].sum()
df_ibov['Setor'] = df_ibov['Setor'].apply(lambda x: x.split('/')[0].rstrip())
df_ibov['Setor'] = df_ibov['Setor'].apply(lambda x: 'Cons N Cíclico' if x == 'Cons N Ciclico' else x)



def definir_evolucao_patrimonial(df_historical_data: pd.DataFrame, df_book_data: pd.DataFrame) -> pd.DataFrame:
    df_historical_data = df_historical_data.set_index('datetime')
    df_historical_data['date'] = df_historical_data.index.date
    df_historical_data = df_historical_data.groupby(['date', 'symbol'])['close'].last().to_frame().reset_index()
    df_historical_data = df_historical_data.pivot(values='close', columns='symbol', index='date')

    df_cotacoes = df_historical_data.copy()
    df_carteira = df_historical_data.copy()

    df_cotacoes = df_cotacoes.replace({0: np.nan}).ffill().fillna(0)
    df_cotacoes.columns = [col.split(':')[-1] for col in df_cotacoes.columns]
    df_carteira.columns = [col.split(':')[-1] for col in df_carteira.columns]
    
    del df_carteira['BVSPX'], df_cotacoes['BVSPX']

    df_book_data['vol'] = df_book_data['vol'] * df_book_data['tipo'].replace({'Compra': 1, 'Venda': -1})
    df_book_data['date'] = pd.to_datetime(df_book_data.date)
    df_book_data.index = df_book_data['date'] 
    df_book_data['date'] = df_book_data.index.date
    
    df_carteira.iloc[:, :] = 0
    for _, row in df_book_data.iterrows():
        df_carteira.loc[df_carteira.index >= row['date'], row['ativo']] += row['vol']
    
    df_patrimonio = df_cotacoes * df_carteira
    df_patrimonio = df_patrimonio.fillna(0)
    df_patrimonio['soma'] = df_patrimonio.sum(axis=1)

    df_ops = df_carteira - df_carteira.shift(1)
    df_ops = df_ops * df_cotacoes
    
    df_patrimonio['evolucao_patrimonial'] = df_patrimonio['soma'].diff() - df_ops.sum(axis=1)           # .plot()
    df_patrimonio['evolucao_percentual'] = (df_patrimonio['evolucao_patrimonial'] / df_patrimonio['soma'])

    ev_total_list = [1]*len(df_patrimonio)
    df_patrimonio['evolucao_percentual'] = df_patrimonio['evolucao_percentual'].fillna(0)
    
    for i, x in enumerate(df_patrimonio['evolucao_percentual'].to_list()[1:]):
        ev_total_list[i+1] = ev_total_list[i] * (1 + x)
        df_patrimonio['evolucao_cum'] = ev_total_list
    
    return df_patrimonio


def slice_df_timedeltas(df: pd.DataFrame, period_string: str) -> pd.DataFrame:
    if period_string == 'ytd':
        correct_timedelta = date.today().replace(month=1, day=1)
        correct_timedelta = pd.Timestamp(correct_timedelta)
    else:
        correct_timedelta = date.today() - TIMEDELTAS[period_string]
    df = df[df.datetime > correct_timedelta].sort_values('datetime')
    return df




layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([html.Img(src='assets/logo_dark.png', height="80px"), "  Stocks Monitor"], className='stocks_monitor_title'),
                                # dbc.Col(, md=7),
                                dbc.Col("", md=2)
                            ])
                        ])
                    ],className='cards_linha1')
                ], xs=12, md=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H3('EGP 778,508.87'),
                                    html.H5('301,361.2408000')
                                ])
                            ])
                        ])
                    ],className='cards_linha1')
                ], md=4)
            ],  className='g-2 my-auto'),

            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H3('EGP'),
                                    html.H5('EGX VOL 24')
                                ])
                            ],className='cards_linha2'), 
                        ], md=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H3('EGP'),
                                    html.H5('Market Cap')
                                ])
                            ],className='cards_linha2')
                        ], md=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H3('USD'),
                                    html.H5('Price(BTC)')
                                ])
                            ], className='cards_linha2')
                        ], md=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H3('EUR'),
                                    html.H5('Trade Value')
                                ])
                            ], className='cards_linha2')
                        ], md=3),
                    ])
                ],md=12),
            ],  className='g-2 my-auto')
        ], xs=4, md=9),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            # html.Legend('Gestão Setorial IBOV', className='textoSecundario'),
                            dbc.Switch(id='radar_switch', value=True, label="Setores IBOV X Carteira"),
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='radar_graph', config={"displayModeBar": False, "showTips": False})
                        ])
                    ])
                ])
            ], className='cardRadar')
        ], xs=12, md=3),
    ],  className='g-2 my-auto'),

    dbc.Row([
        
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='dropdown_card1', className='dbc textoTerciario', value=[], multi=True, options=[]),
                ], sm=12, md=3),
                dbc.Col([
                    dbc.RadioItems(
                        options=[{'label': x, 'value': x} for x in PERIOD_OPTIONS],
                        value='1y',
                        id="period_input",
                        inline=True,
                        className='textoTerciario'
                    ),
                ], sm=12, md=7),
                dbc.Col([
                    html.Span([
                            dbc.Label(className='fa fa-percent '),
                            dbc.Switch(id='profit_switch', value=True, className='d-inline-block ms-1'),
                            dbc.Label(className='fa fa-money')
                    ], className='textoTerciario'),
                ], sm=12, md=2, style={'text-align' : 'end'})
            ],  className='g-2 my-auto'),
        ], xs=12, md=12),
        
        dbc.Col([
            dcc.Graph(id='line_graph', config={"displayModeBar": False, "showTips": False}, style=HEIGHT)    
        ], xs=12, md=12, style={'height' : '100%'}),
    ],  className='g-2 my-auto')
], fluid=True)





# =========  Callbacks  =========== #

# Callback radar graph
@app.callback(
    Output('radar_graph', 'figure'),
    Input('book_data_store', 'data'),
    Input('radar_switch', 'value'),
)
def radar_graph(book_data, comparativo):
    df_registros = pd.DataFrame(book_data)
    df_registros['vol'] = abs(df_registros['vol']) * df_registros['tipo'].replace({'Compra': 1, 'Venda': -1})
    
    if comparativo:
        df_provisorio = df_ibov[df_ibov['Código'].isin(df_registros['ativo'].unique())]
        df_provisorio['Participação2'] = df_provisorio['Participação'].apply(lambda x: x*100/df_provisorio['Participação'].sum())

        ibov_setor = df_provisorio.groupby('Setor')['Participação2'].sum()

        df_registros = df_registros[df_registros['ativo'].isin(df_ibov['Código'].unique())]
        df_registros['Participação'] = df_registros['vol'].apply(lambda x: x*100/df_registros['vol'].sum())

        df_registros = df_registros.groupby('ativo')['Participação'].sum()
        df_registros = pd.DataFrame(df_registros).reset_index()
        df_registros['setores'] = np.concatenate([df_provisorio[df_provisorio['Código'] == ativo]['Setor'].values for ativo in df_registros['ativo']])

        df_registros = df_registros.groupby('setores')['Participação'].sum()

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=ibov_setor, theta=ibov_setor.index, name='IBOV', fill='toself',
                                    hovertemplate ='<b>IBOV</b>'+'<br><b>Participação</b>: %{r:.2f}%'+ '<br><b>Setor</b>: %{theta}<br>', line=dict(color=LINHAS_PREENCHIMENTO_1)))
        fig.add_trace(go.Scatterpolar(r=df_registros, theta=df_registros.index, name='Carteira', fill='toself',
                                    hovertemplate ='<b>CARTEIRA</b>'+'<br><b>Participação</b>: %{r:.2f}%'+ '<br><b>Setor</b>: %{theta}<br>', line=dict(color=LINHAS_PREENCHIMENTO_2)))

    else:
        df_total_ibov = df_ibov.groupby('Setor')['Participação'].sum() * 100
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=df_total_ibov, theta=df_total_ibov.index, name='', fill='toself',
                                    hovertemplate ='<b>IBOV</b>'+'<br><b>Participação</b>: %{r:.2f}%'+ '<br><b>Setor</b>: %{theta}<br>', line=dict(color=LINHAS_PREENCHIMENTO_1)))

    fig.update_traces(line={'shape': 'spline'})
    fig.update_layout(MAIN_CONFIG, showlegend=True, height=TAMANHO_RADAR, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', polar=dict(bgcolor = BACKGROUND_RADAR, angularaxis = dict(tickfont_size = TAMANHO_INDICADORES, color=INDICADORES, gridcolor=LINHA_Y, 
                    linecolor=LINHA_CIRCULAR_EXTERNA), radialaxis=dict(color=VALORES_EIXO_X, gridcolor=LINHAS_CIRCULARES, linecolor=LINHA_X)))


    return fig

# callback line graph
@app.callback(
    Output('line_graph', 'figure'),
    Input('dropdown_card1', 'value'),
    Input('period_input', 'value'),
    Input('profit_switch', 'value'),
    Input('book_data_store', 'data'),
    State('historical_data_store', 'data')
)
def func_card1(dropdown, period, profit_switch, book_info, historical_info):
    if dropdown == None:
        return no_update
    if type(dropdown) != list: dropdown = [dropdown]
    dropdown = ['BVSPX'] + dropdown
    
    df_hist = pd.DataFrame(historical_info)
    df_hist['datetime'] = pd.to_datetime(df_hist['datetime'], format='%Y-%m-%d %H:%M:%S')
    df_hist = slice_df_timedeltas(df_hist, period)

    fig = go.Figure()

    if profit_switch:
        df_book = pd.DataFrame(book_info)  
        df_patrimonio = definir_evolucao_patrimonial(df_hist, df_book)
        
        fig.add_trace(go.Scatter(x=df_patrimonio.index, y=(df_patrimonio['evolucao_cum']- 1) * 100, mode='lines', name='Evolução Patrimonial', line=dict(color=LINHA_EVOLUCAO_PATRIMONIAL)))
    
    else:
        df_hist = df_hist[df_hist['symbol'].str.contains('|'.join(dropdown))]
        i=0
        for ticker in dropdown:
            i+=1
            df_aux = df_hist[df_hist.symbol.str.contains(ticker)]
            df_aux.dropna(inplace=True)
            df_aux.close = df_aux.close / df_aux.close.iloc[0] - 1
            fig.add_trace(go.Scatter(x=df_aux.datetime, y=df_aux.close*100, mode='lines', name=ticker, line=dict(color=LISTA_DE_CORES_LINHAS[i-1])))
    
    fig.update_layout(MAIN_CONFIG_2, yaxis={'ticksuffix': '%'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_xaxes(tickfont=dict(family='Courier', size=AXIS_FONT_SIZE, color=AXIS_COLOR), gridcolor=LINHAS_DE_GRADE)
    fig.update_yaxes(tickfont=dict(family='Courier', size=AXIS_FONT_SIZE, color=AXIS_COLOR), gridcolor=LINHAS_DE_GRADE, zerolinecolor=LINHA_ZERO_X)
    
    return fig

# callback para atulizar o dropdown
@app.callback(
    Output('dropdown_card1', 'value'),
    Output('dropdown_card1', 'options'),
    Input('book_data_store', 'data'),
)
def atualizar_dropdown(book):
    df = pd.DataFrame(book)
    unique = df['ativo'].unique()
    
    return [unique[0], [{'label': x, 'value': x} for x in unique]]