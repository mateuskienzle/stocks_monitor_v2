from dash import html, dcc, Input, Output, State, no_update, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime, date

from app import *

from datetime import date


layout = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Cadastro de ativos"), className='modal_header'),
    dbc.ModalBody([
        dbc.Row([
            dbc.Col([
                dbc.Input(id="nome_ativo", placeholder="Nome", type='text')
            ]),
            dbc.Col([
                dbc.Input(id="preco_ativo", placeholder="Preço (R$)", type='number', min=0, step=0.01)
            ])

        ]),
        dbc.Row([
            dbc.Col([
                "Data:   ",
                dcc.DatePickerSingle(
                id='data_ativo',
                className='dbc',
                min_date_allowed=date(2005, 1, 1),
                max_date_allowed=date.today(),
                initial_visible_month=date(2017, 8, 5),
                date=date.today()
                ),
            ], sm=12, md=6),
            dbc.Col([
                dbc.Input(id="quantidade_ativo", placeholder="Quantidade", type='number', min=0, step=1),
            ])
        ], style={'margin-top' : '1rem'}),
        dbc.Row([
            # dbc.Col([
            #     html.Img(id='imagem_ativo', src="https://petrobras.com.br/sitepetrobras/imgs/bg/logo-social.png", style={'width' : '30%', 'margin-top' : '1rem', 'border-radius' : '15%'})
            # ]),
            dbc.Col([
                dbc.RadioItems(id='compra_venda_radio', options=[{"label": "Compra", "value": 'Compra'}, {"label": "Venda", "value": 'Venda'}], value='Compra'),
            ]),
        ])
    ], className='modal_body'),
    dbc.ModalFooter([
        dbc.Row([
            dbc.Col([dbc.Button("Salvar", id="submit_cadastro")])
        ])
    ], className='modal_footer'),
],id="modal", is_open=False, size='lg', centered=True)



# Callbacks =======================
# Callback para checar o loading state -----
@app.callback(
    Output('submit_cadastro', 'children'),

    Input('submit_cadastro', 'n_clicks'),
    Input('add_button', 'n_clicks'),
    # Input('positioned_toast', 'icon'),
)
def add_spinner(n, n2):
    trigg_id = callback_context.triggered[0]['prop_id'].split('.')[0]

    if trigg_id == 'submit_cadastro':
        return [dbc.Spinner(size="sm"), "  Carregando informações do ativo..."]
    elif trigg_id == 'add_button':
        return "Salvar"
    else:
        return no_update

# Callback para limpar infos do modal -----
@app.callback(
    Output('nome_ativo', 'value'),
    Output('preco_ativo', 'value'),
    Output('data_ativo', 'date'),
    Output('quantidade_ativo', 'value'),

    Input('positioned_toast', 'header')
)
def reset_data_modal(icon):
    trigg_id = callback_context.triggered[0]['prop_id'].split('.')[0]

    if trigg_id != 'positioned_toast':
        return no_update
    else:
        if "Confirmação" in icon:
            return [None, None, date.today(), None]
        else:
            return no_update
    