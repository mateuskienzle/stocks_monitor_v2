from dash import html, dcc
import dash
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px


from app import app
from components import modal_adicao


layout = dbc.Container([
    #Linha 1
    dbc.Row([
    modal_adicao.layout,
        dbc.Col([
            dbc.Button("Home", href='/home', className='header_icon')
        ], md=1), 
        dbc.Col([
            dbc.Button("Wallet", href='/wallet', className='header_icon')
        ], md=1),
        dbc.Col([
            dbc.Button("Add", href='', id='add_button', className='header_icon')
        ], md=1),
        html.Hr(style={'color' : 'rgba(255, 255, 255, 0.6)'})
], className='g-2 my-auto'),

], fluid=True)