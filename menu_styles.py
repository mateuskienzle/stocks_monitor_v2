COR_LEGENDA = 'rgba(255,255,255,0.4)'

#menu radar graph
INDICADORES = 'rgba(255,255,255,0.4)'
BACKGROUND_RADAR = '#5d3b97'  
LINHA_X = 'white'
LINHA_Y = 'white'
LINHAS_CIRCULARES = 'black'
LINHA_CIRCULAR_EXTERNA = 'black'
LINHAS_PREENCHIMENTO_1 = 'white'
LINHAS_PREENCHIMENTO_2 = 'black'
CAIXA_LEGENDA = 'rgba(255,255,255,0.1)'
AXIS_X_VALUES_COLOR = 'rgba(0,0,0,0)'
TAMANHO_INDICADORES = 15
TAMANHO_RADAR = 280

#menu line graph
AXIS_FONT_SIZE = 22
AXIS_VALUES_COLOR = 'rgba(255,255,255,0.4)'
LINHAS_DE_GRADE = 'rgba(255,255,255,0.1)'
LINHA_ZERO_X = 'rgba(255,255,255,0.2)'
LINHA_EVOLUCAO_PATRIMONIAL = '#5d3b97'
LISTA_DE_CORES_LINHAS = ['#670067', '#9400d3', '#766ec5', '#120a8f', '#825280', '#00b6ff', '#00aaff', 'white']
HOVER_LINE_GRAPH = {
        "bgcolor":"#5d3b97",
        "font" : {'color':COR_LEGENDA}
}

HEIGHT={'height': '100%'}
MAIN_CONFIG = {
    "hovermode": "x unified",
    "legend": {"yanchor":"top", 
                "y":1.0, 
                "xanchor":"left",
                "x":1.0,
                "title": {"text": None},
                "bgcolor": CAIXA_LEGENDA},
    "font" : {'color':COR_LEGENDA},
    "margin": {"l":0, "r":0, "t":10, "b":0},
}
MAIN_CONFIG_2 = {
    "hovermode": "x unified",
    "legend": {"bgcolor": CAIXA_LEGENDA},
    "font" : {'color': COR_LEGENDA},
    "margin": {"l":0, "r":0, "t":10, "b":0},
}