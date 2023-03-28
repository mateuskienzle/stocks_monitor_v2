import yfinance as yf
import pandas as pd
import requests as r

class Asimov_finance: 
    def __init__(self):
        self.start = '2011-01-01'
        '''
        period : str
                Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                Either Use period parameter or use start and end
        '''
    
    # def get_cdi(self) -> pd.DataFrame:
    #     url = 'https://www.valor.srv.br/indices/cdi.php'
    #     html = r.get(url).content
    #     df_list = pd.read_html(html, decimal=',', thousands='.')
    #     return df_list[0]

    # def get_inflation_rates(self):
    #     url = 'https://www.infomoney.com.br/ferramentas/inflacao/'
    #     html = r.get(url).content
    #     df_list = pd.read_html(html)

    # def get_ibovespa(   # delete function, it may not make sense
    #     self, 
    #     period:list=None,
    #     ) -> pd.DataFrame:
    #     ibovespa = yf.Ticker("^BVSP")
    #     if not period: 
    #         return ibovespa.history(start=self.start).pct_change()
    #     else: 
    #         return ibovespa.history(period=period).pct_change()

    def get_symbol_object(self, ticker) -> yf.ticker.Ticker:
        symbol_object = yf.Ticker(ticker)
        hist = symbol_object.history(start=self.start)
        if hist.empty:
            if ".SA" in ticker: return None
            else:
                return self.get_symbol_object(ticker + ".SA")
        else:
            if hist.empty:
                return None
            else:
                return symbol_object

    # def get_symbol_info(self, ticker_string) -> dict:
    #     symbol_object = self.get_symbol_object(ticker_string)

    #     if symbol_object == None: return {}
    #     else:
    #         keys = ['logo_url']
    #         return {key: symbol_object.info[key] for key in keys}

    # def get_history_data(self, ticker) -> pd.DataFrame:
    #     call_string = ''
    #     if type(ticker) == list:
    #         ticker = ['msft', 'aapl', 'goog']
    #         for t in ticker:
    #             call_string += f'{t} '  
    #     ticker = self.get_symbol_object(ticker)

    #     if ticker == None: return None
    #     else:
    #         return ticker.history(start=self.start)

    # def get_news(ticker) -> pd.DataFrame:
    #     news = yf.Ticker(ticker).news
    #     return news  







