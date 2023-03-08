from dash import html, dcc
import dash
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px


from app import app


layout = dbc.Container([
    #Linha 1
    dbc.Row([
        dbc.Col([
            dbc.Button("Home", href='/home', className='header_icon')
        ], md=1), 
        dbc.Col([
            dbc.Button("Add", href='', className='header_icon')
        ], md=1),
        html.Hr(style={'color' : 'rgba(255, 255, 255, 0.6)'})
    ], className='g-2 my-auto'),

], fluid=True)