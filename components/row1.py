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
from functions import *



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
                ], xs=12, md=7),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Legend('CARTEIRA:', className='textoSecundario'),
                                ], md=6),
                                dbc.Col([
                                    html.H5("R$" + '{:,.2f}'.format(df_book_data['valor_total'].sum() - df_compra_e_venda['valor_total']['Venda']), className='textoSecundario'),
                                    html.H5([html.I(className='fa fa-angle-up'), "  ", " 7.19%"], className='textoQuartenarioVerde')
                                ], md=6)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Legend('IBOV: ', className='textoQuartenario')
                                ], md=6),
                                dbc.Col([
                                    
                                ], md=6, id='card_ibov')
                            ])
                        ])
                    ],className='card2_linha1')
                ], md=5)
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
], fluid=True)




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

#callback para atualizar os cards
@app.callback(
    Output('card_ibov', 'children'),
    Output('cards_ativos', 'children'),
    Input('book_data_store', 'data'),
    Input('period_input', 'value'),
    Input('dropdown_card1', 'value'),
    State('historical_data_store', 'data')
)

def atualizar_cards_ativos(book_data, period, dropdown, historical_data):
    if dropdown == None:
        return no_update
    if type(dropdown) != list: dropdown = [dropdown]
    dropdown = ['BVSPX'] + dropdown
    
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
    ativos_existentes['BVSPX'] = 1 #botei 1 pq era só pra adicionar um valor qualquer, o que importa é a chave 'BVSPX'

    # print('CHEGOU AQUI')
    

    
    # df_ibov = df_hist[df_hist['symbol'].str.contains(' '.join(['IBOV']))]
    # valor_atual_ibov = df_ibov['close'].iloc[-1]
    # diferenca_ibov = valor_atual_ibov/df_ibov['close'].iloc[0]
    # diferenca_ibov = diferenca_ibov*100 - 100


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
    
    # import pdb
    # pdb.set_trace()

    
    seta_crescendo = ['fa fa-angle-up', 'textoQuartenarioVerde',]
    seta_caindo = ['fa fa-angle-down', 'textoQuartenarioVermelho']

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


    # import pdb
    # pdb.set_trace()

    #Graficos
    

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
                                        html.H5(["R$",'{:,.2f}'.format(lista_valores_ativos[i][1]), " "], className='textoTerciario'),
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
                                         html.H5(["R$",'{:,.2f}'.format(lista_valores_ativos[i][1]), " "], className='textoTerciario'),
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
    
    valor_ibov = [html.H5(["R$",'{:,.2f}'.format(lista_valores_ativos[-1][1], 2), " "], className='textoQuartenario'),
                html.H5([html.I(className=lista_valores_ativos[-1][3]), " ", lista_valores_ativos[-1][2].round(2), "%"], className=lista_valores_ativos[-1][4])]
                 
    return valor_ibov, card_ativos
