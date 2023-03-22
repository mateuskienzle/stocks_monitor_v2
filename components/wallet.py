from dash import html, dcc, no_update, callback_context
from dash.dependencies import Input, Output, State, ALL
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from pandas.tseries.offsets import DateOffset
from datetime import date
import json

from app import *
from yfinance_class.y_class import Asimov_finance
from components.modal_adicao import *

financer = Asimov_finance()

HEIGHT={'height': '100%'}


def generate_card(info_do_ativo):
    new_card =  dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-list-alt', style={"fontSize": '85%'}), " Nome: "], className='textoQuartenario'),
                                        html.H5(str(info_do_ativo['ativo']), className='textoQuartenarioBranco')
                                    ], md=2, style={'text-align' : 'left'}),                              
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-database', style={"fontSize": '85%'}), " Quantidade: "], className='textoQuartenario'),
                                        html.H5(str(info_do_ativo['vol']), className='textoQuartenarioBranco')
                                    ], md=2, style={'text-align' : 'left'}),
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-money', style={"fontSize": '85%'}), " Unitário: "], className='textoQuartenario'),
                                        html.H5('{:,.2f}'.format(info_do_ativo['preco']), className='textoQuartenarioBranco')
                                        # " Valor unitário: R$" + '{:,.2f}'.format(info_do_ativo['preco'])
                                    ], md=2, style={'text-align' : 'left'}),
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-calendar', style={"fontSize": '85%'}), " Data: "], className='textoQuartenario'),
                                        html.H5(str(info_do_ativo['date'])[:10], className='textoQuartenarioBranco')
                                    ], md=2, style={'text-align' : 'left'}),
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-handshake-o', style={"fontSize": '85%'}), " Tipo: "], className='textoQuartenario'),
                                        html.H5(str(info_do_ativo['tipo']), className='textoQuartenarioBranco')
                                    ], md=2, style={'text-align' : 'left'}),
                                    dbc.Col([
                                        html.H5([html.I(className='fa fa-money', style={"fontSize": '85%'}), " Total: "], className='textoQuartenario'),
                                        html.H5('{:,.2f}'.format(info_do_ativo['preco']*info_do_ativo['vol']), className='textoQuartenarioBranco'),
                                    ], md=2, style={'text-align' : 'left'}),
                                ]),
                            ], md=11, xs=6, style={'text-align' : 'left'}),
                            dbc.Col([
                                dbc.Button([html.I(className = "fa fa-trash header-icon", 
                                                    style={'font-size' : '150%'})],
                                                    id={'type': 'delete_event', 'index': info_do_ativo['id']},
                                                    style={'background-color' : 'transparent', 'border-color' : 'transparent', 'padding' : '0px'}
                                                ), 
                            ], md=1, xs=12, style={'text-align' : 'right'})
                        ])
                    ])
                ], class_name=info_do_ativo['class_card'])
            ])
        ], className='g-2 my-auto')

    return new_card




def generate_list_of_cards(df):
    lista_de_dicts = []
    for row in df.index:
        infos = df.loc[row].to_dict()
        #altera nome da classe do card se for compra ou venda
        if infos['tipo'] == 'Compra':
            infos['class_card'] = 'card_compra'
        else:
            infos['class_card'] = 'card_venda'
        infos['id'] = row
        lista_de_dicts.append(infos)

    lista_de_cards = []
    for dicio in lista_de_dicts:
        card = generate_card(dicio)
        lista_de_cards.append(card)
    return lista_de_cards





layout = dbc.Container([

    dbc.Row([
        dbc.Col([
    
        ], md=12, id='layout_wallet', style={"height": "100%", "maxHeight": "36rem", "overflow-y": "auto"})
    ], className='g-2 my-auto')

    
],fluid=True),


@app.callback(
    Output('layout_wallet', 'children'),
    Input('layout_data', 'data')
)
def test1(data):
    return data

@app.callback(
    Output('modal', 'is_open'),
    # Output("positioned_toast", "is_open"),
    # Output('positioned_toast', 'header'),
    # Output('positioned_toast', 'children'),
    # Output('positioned_toast', 'icon'),
    # Output('imagem_ativo', 'src'),
    Output('book_data_store', 'data'),
    Output ('layout_data', 'data'),

    Input('add_button', 'n_clicks'),
    Input('submit_cadastro', 'n_clicks'),
    Input('book_data_store', 'data'),
    Input({'type': 'delete_event', 'index': ALL}, 'n_clicks'),

    State('nome_ativo', 'value'),
    State('modal', 'is_open'),
    State('compra_venda_radio', 'value'),
    State('preco_ativo', 'value'),
    State('data_ativo', 'date'),
    State('quantidade_ativo', 'value'),
)
def func_modal(n1, n2, data, event, ativo, open, radio, preco, periodo, vol):
    trigg_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    # print('TRIGG_ID', trigg_id)
    # print('OPT4', callback_context.triggered[0])    # dict['value'] == None -> ignorar
                                                    # dict['value'] != None -> clicado

    # return_default = ['', '' , '']
    # return_fail_inputs = ['Não foi possível registrar a sua ação!', 
    #                 'É necessário preencher todos os campos do Formulário.',
    #                 'primary']
    # return_fail_ticker = return_fail_inputs.copy()
    # return_fail_ticker[1] = 'É necessário inserir um Ticker válido.'
    # return_compra = ['Confirmação de Adição', 'Registro de COMPRA efetivado!', 'success']
    # return_venda =  ['Confirmação de Remoção', 'Registro de VENDA efetivado!', 'warning']
    
    df = pd.DataFrame(data)

    lista_de_cards = generate_list_of_cards(df)
    # Casos de trigg
    # 0. Trigg automático
    if trigg_id == '':
        return [open, data, lista_de_cards]

    # 1. Botão de abrir modal
    if trigg_id == 'add_button':
        return [not open, data, lista_de_cards]
    
    # 2. Salvando ativo
    elif trigg_id == 'submit_cadastro':  # Corrigir caso de erro - None
        if None in [ativo, preco, vol] and open:
            return [open, data, lista_de_cards]
        else:
            ativo = ativo.upper()
            ticker = financer.get_symbol_object(ativo)
            if ticker:
                df = pd.DataFrame(data)
                exchange = 'BMFBOVESPA'
                preco = round(preco, 2)
                df.loc[len(df)] = [periodo, preco, radio, ativo, exchange ,vol, vol*preco]    
                df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
                df.reset_index(drop=True, inplace=True)
                df = df.sort_values(by='date', ascending=True)

                df.to_csv('book_data.csv')
                data = df.to_dict()
                
                lista_de_cards = generate_list_of_cards(df)

                return [not open, data, lista_de_cards]
            else:   
                return [not open, data, lista_de_cards]

    # 3. Caso de delete de card
    if 'delete_event' in trigg_id:
        trigg_dict = callback_context.triggered[0]

        if trigg_dict['value'] == None:
            return [open, data, lista_de_cards]

        else:
            trigg_id = json.loads(trigg_id)
            df.drop([trigg_id['index']], inplace=True)
            
            df.to_csv('book_data.csv')
            data = df.to_dict()

            lista_de_cards = generate_list_of_cards(df)

            return [open, data, lista_de_cards]

    return [open, data, lista_de_cards]