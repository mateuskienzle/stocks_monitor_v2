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
from menu_styles import *



offsets = [DateOffset(days=5), DateOffset(months=1), DateOffset(months=3), DateOffset(months=6), DateOffset(years=1), DateOffset(years=2)] 
delta_titles = ['5 dias', '1 mês', '3 meses', '6 meses', '1 ano', '2 anos', 'Ano até agora']
PERIOD_OPTIONS = ['5d','1mo','3mo','6mo','1y','2y', 'ytd']

TIMEDELTAS = {x: y for x, y in zip(PERIOD_OPTIONS, offsets)}
TITLES = {x: y for x, y in zip(PERIOD_OPTIONS, delta_titles)}



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
                                dbc.Col([html.Img(src='assets/logo_dark.png', height="65px"), "  Stocks Monitor"], className='textoPrincipal'),
                            ])
                        ])
                    ],className='card1_linha1')
                ], xs=12, md=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Legend('CARTEIRA: R$2500.00', className='textoSecundario'),
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Legend('IBOV: R$102.932,38', className='textoQuartenario')
                                ])
                            ])
                        ])
                    ],className='card2_linha1')
                ], md=4)
            ],  className='g-2 my-auto'),

            dbc.Row([
                dbc.Col([
                    
                ],md=12, id='cards_ativos'),
            ],  className='g-2 my-auto')
        ], xs=12, md=9),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Switch(id='radar_switch', value=True, label="Setores IBOV X Carteira", className='textoTerciario'),
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
                    dcc.Dropdown(id='dropdown_card1', value=[], multi=True, options=[]),
                ], sm=12, md=3),
                dbc.Col([
                    dbc.RadioItems(
                        options=[{'label': x, 'value': x} for x in PERIOD_OPTIONS],
                        value='1y',
                        id="period_input",
                        inline=True,
                        className='textoTerciario',
                    ),
                ], sm=12, md=7),
                dbc.Col([
                    html.Span([
                            dbc.Label(className='fa fa-money'),
                            dbc.Switch(id='profit_switch', value=True, className='d-inline-block ms-1'),
                            dbc.Label(className='fa fa-percent '),
                    ], className='textoTerciarioSwitchLineGraph'),
                ], sm=12, md=2, style={'text-align' : 'end'})
            ],  className='g-2 my-auto'),
        ], xs=12, md=12),     
    ],  className='g-2 my-auto'),

    dbc.Row([
        dbc.Col([
            # dbc.Row([
            #     dbc.Col([
            #         html.Legend("Desempenho de ativos", id='title_line_graph', className='textoTerciario', style={'margin-top' : '20px'})    
            #     ], xs=12, md=12)
            # ]),
            # dbc.Row([
            #     dbc.Col([
                dcc.Graph(id='line_graph', config={"displayModeBar": False, "showTips": False}, className='graph_line')    
            ], xs=12, md=12,)
        #     ])
        # ]),
    ])
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
        fig.add_trace(go.Scatterpolar(r=df_total_ibov, theta=df_total_ibov.index, name='Carteira', fill='toself',
                                    hovertemplate ='<b>IBOV</b>'+'<br><b>Participação</b>: %{r:.2f}%'+ '<br><b>Setor</b>: %{theta}<br>', line=dict(color=LINHAS_PREENCHIMENTO_1)))

    fig.update_traces(line={'shape': 'spline'})
    fig.update_layout(MAIN_CONFIG, showlegend=True, height=TAMANHO_RADAR, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', polar=dict(bgcolor = BACKGROUND_RADAR, angularaxis = dict(tickfont_size = TAMANHO_INDICADORES, color=INDICADORES, gridcolor=LINHA_Y, 
                    linecolor=LINHA_CIRCULAR_EXTERNA), radialaxis=dict(color=AXIS_X_VALUES_COLOR, gridcolor=LINHAS_CIRCULARES, linecolor=LINHA_X)))


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
    
    # print('CHEGOU AQUI')
    # print(dropdown)
    # import pdb
    # pdb.set_trace()

    df_hist = pd.DataFrame(historical_info)
    df_hist['datetime'] = pd.to_datetime(df_hist['datetime'], format='%Y-%m-%d %H:%M:%S')
    df_hist = slice_df_timedeltas(df_hist, period)

    fig = go.Figure()

    if profit_switch:
        df_hist = df_hist[df_hist['symbol'].str.contains('|'.join(dropdown))]
        i=0
        for ticker in dropdown:
            i+=1
            df_aux = df_hist[df_hist.symbol.str.contains(ticker)]
            df_aux.dropna(inplace=True)
            df_aux.close = df_aux.close / df_aux.close.iloc[0] - 1
            fig.add_trace(go.Scatter(x=df_aux.datetime, y=df_aux.close*100, mode='lines', name=ticker, line=dict(color=LISTA_DE_CORES_LINHAS[i-1])))
        
    else:
        df_book = pd.DataFrame(book_info)  
        df_patrimonio = definir_evolucao_patrimonial(df_hist, df_book)
        
        fig.add_trace(go.Scatter(x=df_patrimonio.index, y=(df_patrimonio['evolucao_cum']- 1) * 100, mode='lines', name='Evolução Patrimonial', line=dict(color=LINHA_EVOLUCAO_PATRIMONIAL), fill='tozeroy', fillcolor=PREENCHIMENTO_LINE_GRAPH))
    
        
    
    fig.update_layout(MAIN_CONFIG_2, showlegend=True, yaxis={'ticksuffix': '%'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hoverlabel=HOVER_LINE_GRAPH)
    fig.update_xaxes(tickfont=dict(family='Nexa', size=AXIS_FONT_SIZE, color=AXIS_VALUES_COLOR), gridcolor=LINHAS_DE_GRADE)
    fig.update_yaxes(tickfont=dict(family='Nexa', size=AXIS_FONT_SIZE, color=AXIS_VALUES_COLOR), gridcolor=LINHAS_DE_GRADE, zerolinecolor=LINHA_ZERO_X)
    
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


#callback para atualizar os cards
@app.callback(
    Output('cards_ativos', 'children'),
    Input('book_data_store', 'data'),
    Input('period_input', 'value'),
    Input('dropdown_card1', 'value'),
    State('historical_data_store', 'data')
)

def atualizar_cards_ativos(book_data, period, dropdown, historical_data):
    df_book = pd.DataFrame(book_data)
    df_hist = pd.DataFrame(historical_data)

    df_book['datetime'] = pd.to_datetime(df_book['date'], format='%Y-%m-%d %H:%M:%S')

    df2 = df_book.groupby(by=['ativo', 'tipo'])['vol'].sum()

    diferenca_ativos = {}
    for ativo, new_df in df2.groupby(level=0):
        compra, venda = 0, 0
        try:
            compra = new_df.xs((ativo, 'Compra'))
        except: pass
        try:
            venda = new_df.xs((ativo, 'Venda'))
        except: pass
        diferenca_ativos[ativo] = compra - venda

    ativos_existentes = dict((k, v) for k, v in diferenca_ativos.items() if v >= 0)

    if period == 'ytd':
        correct_timedelta = date.today().replace(month=1, day=1)
        correct_timedelta = pd.Timestamp(correct_timedelta)
    else:
        correct_timedelta = date.today() - TIMEDELTAS[period]

    dict_valores = {}

    for key, value in ativos_existentes.items():
        df_auxiliar = (df_hist[df_hist.symbol.str.contains(key)])
        df_auxiliar['datetime'] = pd.to_datetime(df_auxiliar['datetime'], format='%Y-%m-%d %H:%M:%S')
        df_periodo = df_auxiliar[df_auxiliar['datetime'] > correct_timedelta]
        valor_atual = df_periodo['close'].iloc[-1]
        diferenca_periodo= valor_atual/df_periodo['close'].iloc[0]
        dict_valores[key] = valor_atual, diferenca_periodo
        dfativos= pd.DataFrame(dict_valores).T.rename_axis('ticker').add_prefix('Value').reset_index()
        dfativos['Value1']= dfativos['Value1']*100 - 100

    
    seta_crescendo = ['fa fa-angle-up', 'textoTerciarioVerde']
    seta_caindo = ['fa fa-angle-down', 'textoTerciarioVermelho']

    lista_valores_ativos = []
    lista_tags = []
    for ativo in range(len(dfativos)):
        tag_ativo = dfativos.iloc[ativo][0]
        lista_tags.append(tag_ativo)
        valor_ativo = dfativos.iloc[ativo][1]
        variacao_ativo = dfativos.iloc[ativo][2]
        if variacao_ativo < 0:
            lista_valores_ativos.append([tag_ativo, valor_ativo, variacao_ativo, seta_caindo[0], seta_caindo[1]])
        else: 
            lista_valores_ativos.append([tag_ativo, valor_ativo, variacao_ativo, seta_crescendo[0], seta_crescendo[1]])


    #Graficos
    
    # print('CHEGOU AQUI')
    # print(dropdown)
    # import pdb
    # pdb.set_trace()

    df_hist = pd.DataFrame(historical_data)
    df_hist['datetime'] = pd.to_datetime(df_hist['datetime'], format='%Y-%m-%d %H:%M:%S')
    df_hist = slice_df_timedeltas(df_hist, period)

    
    

    df_hist = df_hist[df_hist['symbol'].str.contains('|'.join(lista_tags))]

    lista_graficos = []
    for n, ticker in enumerate(lista_tags):
        fig = go.Figure()
        df_aux = df_hist[df_hist.symbol.str.contains(ticker)]
        df_aux.dropna(inplace=True)
        df_aux.close = df_aux.close / df_aux.close.iloc[0] - 1

        fig.add_trace(go.Scatter(x=df_aux.datetime, y=df_aux.close*100, mode='lines', name=ticker,line=dict(color=CARD_GRAPHS_LINE_COLOR), hoverinfo = "skip"))

        fig.update_layout(MAIN_CONFIG_3, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        
        lista_graficos.append(fig)

    # import pdb
    # pdb.set_trace()




  
    lista_colunas = []
    if len(lista_valores_ativos) <= 4:
        for i in range(len(lista_valores_ativos)):
            col = dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        html.Legend(lista_valores_ativos[i][0], className='textoQuartenario'),
                                        
                                    ], md=4),
                                    dbc.Col([
                                        dcc.Graph(figure=lista_graficos[i], config={"displayModeBar": False, "showTips": False}, className='graph_cards'),
                                    ], md=8)
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        html.H5(["R$",lista_valores_ativos[i][1], " "], className='textoTerciario'),
                                        html.H5([html.I(className=lista_valores_ativos[i][3]), " ", lista_valores_ativos[i][2].round(2), "%"], className=lista_valores_ativos[i][4])
                                    ])
                                ])
                            ])
                        ],className='cards_linha2'), 
                    ], md=3)
            
            lista_colunas.append(col)
    else: 
        for i in range(4):
            col = dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        html.Legend(lista_valores_ativos[i][0], className='textoQuartenario'),
                                        
                                    ], md=4),
                                    dbc.Col([
                                        dcc.Graph(figure=lista_graficos[i], config={"displayModeBar": False, "showTips": False}, className='graph_cards'),
                                    ], md=8)
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                        html.H5(["R$",lista_valores_ativos[i][1], " "], className='textoTerciario'),
                                        html.H5([html.I(className=lista_valores_ativos[i][3]), " ", lista_valores_ativos[i][2].round(2), "%"], className=lista_valores_ativos[i][4])
                                    ])
                                ])
                            ])
                        ],className='cards_linha2'), 
                    ], md=3)
            
            lista_colunas.append(col)

    card_ativos= dbc.Row([
                    *lista_colunas
                ])
                 
    return card_ativos