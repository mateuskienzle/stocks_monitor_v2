import yfinance as yf

# NOTES
'''
1. O yf.Ticker não diferencia chars minusculos e maiusculos
2. msft.info pode acusar se o ativo existe ou não
3. É possível identificar qual o tipo da companhia através do mstf.info em "industry"
'''

msft = yf.Tickers('ITUB4.SA', "MGLU3.SA")
a = msft.info
hist = msft.history(period="1y")
msft.history_metadata

# da pra pegar varios tickers de uma vez
tickers = yf.Tickers('msft aapl goog')
tickers.tickers['GOOG'].actions
tickers.news()
li = []

for key in msft.history_metadata.keys():
    li.append(key)

msft.actions
msft.dividends
msft.splits
msft.capital_gains
msft.shares
msft.cashflow
msft.quarterly_cashflow

msft.major_holders
msft.institutional_holders
msft.mutualfund_holders

msft.earnings
msft.quarterly_earnings

msft.news

# Exemplo de erro
ticker = yf.Ticker('CArlos lacerda')
ticker_hist = ticker.history(period='max')
ticker.history_metadata

# Anotações pré projeto
# Se o ativo não existir, ao acionar a função ticker.history(period='max'), o yfinance deve retornar:
'''
Got error from yahoo api for ticker CARLOS LACERDA, Error: {'code': 'Not Found', 'description': 'No data found, symbol may be delisted'}
- CARLOS LACERDA: No timezone found, symbol may be delisted
'''
# Podemos usar isso para filtrar se o ativo adicionado existe ou não.
# Ou se fizer o ticker.info, recebe o retorno
'''
- PETR4: No summary info found, symbol may be delisted
'''
# é possível utilizar a função assert
'''
assert(ticker.info is not None and ticker.info != {})
'''