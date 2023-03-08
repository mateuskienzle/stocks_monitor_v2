from dash import html, dcc, Input, Output, State, no_update
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from app import *


#menu radar graph
INDICADORES = 'white'
BACKGROUND_RADAR = '#670067'  
LINHA_X = '#c1496b'
LINHA_Y = '#c1496b'
LINHAS_CIRCULARES = 'white'
LINHA_CIRCULAR_EXTERNA = 'white'
LINHAS_PREENCHIMENTO = '#100731'
CAIXA_LEGENDA = '#670067'
VALORES_EIXO_X = 'white'
TAMANHO_INDICADORES = 15
TAMANHO_RADAR = 200


HEIGHT={'height': '100%'}
MAIN_CONFIG = {
    "hovermode": "x unified",
    # "legend": {"yanchor":"top", 
    #             "y":1.0, 
    #             "xanchor":"left",
    #             "x":0.8,
    #             "title": {"text": None},
    #             "font" :{"color":"white"},
    #             "bgcolor": CAIXA_LEGENDA},
    "margin": {"l":0, "r":0, "t":10, "b":0},
}





df_ibov = pd.read_csv('tabela_ibov.csv')

df_ibov['Part. (%)'] = pd.to_numeric(df_ibov['Part. (%)'].str.replace(',','.'))
df_ibov['Qtde. Teórica'] = pd.to_numeric(df_ibov['Qtde. Teórica'].str.replace('.', ''))
df_ibov['Participação'] = df_ibov['Qtde. Teórica'] / df_ibov['Qtde. Teórica'].sum()
df_ibov['Setor'] = df_ibov['Setor'].apply(lambda x: x.split('/')[0].rstrip())
df_ibov['Setor'] = df_ibov['Setor'].apply(lambda x: 'Cons N Cíclico' if x == 'Cons N Ciclico' else x)



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
                ], md=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H3('EGP EGP 778,508.87'),
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
                            dbc.Switch(id='ibov_switch', value=True, label="Setores IBOV X Carteira"),
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
], fluid=True)




















# =========  Callbacks  =========== #
# Callback radar graph
@app.callback(
    Output('radar_graph', 'figure'),
    Input('book_data_store', 'data'),
    Input('ibov_switch', 'value'),
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
        fig.add_trace(go.Scatterpolar(r=ibov_setor, theta=ibov_setor.index, name='', fill='toself',
                                    hovertemplate ='<b>IBOV</b>'+'<br><b>Participação</b>: %{r:.2f}%'+ '<br><b>Setor</b>: %{theta}<br>'))
        fig.add_trace(go.Scatterpolar(r=df_registros, theta=df_registros.index, name='', fill='toself',
                                    hovertemplate ='<b>CARTEIRA</b>'+'<br><b>Participação</b>: %{r:.2f}%'+ '<br><b>Setor</b>: %{theta}<br>'))

    else:
        df_total_ibov = df_ibov.groupby('Setor')['Participação'].sum() * 100
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=df_total_ibov, theta=df_total_ibov.index, name='', fill='toself',
                                    hovertemplate ='<b>IBOV</b>'+'<br><b>Participação</b>: %{r:.2f}%'+ '<br><b>Setor</b>: %{theta}<br>'))

    fig.update_traces(line={'shape': 'spline', 'color' : LINHAS_PREENCHIMENTO})
    fig.update_layout(MAIN_CONFIG, height=TAMANHO_RADAR, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', polar=dict(bgcolor = BACKGROUND_RADAR, angularaxis = dict(tickfont_size = TAMANHO_INDICADORES, color=INDICADORES, gridcolor=LINHA_Y, 
                    linecolor=LINHA_CIRCULAR_EXTERNA), radialaxis=dict(color=VALORES_EIXO_X, gridcolor=LINHAS_CIRCULARES, linecolor=LINHA_X)))


    return fig