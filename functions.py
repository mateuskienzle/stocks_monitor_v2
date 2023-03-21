import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset
from datetime import date


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

try:
    df_book_data = pd.read_csv('book_data.csv', index_col=0)
except:
    columns = ['date', 'preco', 'tipo', 'ativo', 'exchange', 'vol', 'valor_total']
    df_book_data = pd.DataFrame(columns=columns)

df_compra_e_venda = df_book_data.groupby('tipo').sum()