import pandas as pd
import yfinance as yf
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests, time, datetime, random, json



class Scrapy():
    def __init__(self):
        #self.urls 就是宣告出一個變數並且給他數值 然後指定給這個類 之後只要執行這個function 這個變數就會暫存在這個類底下
        self.urls = {
                "listed": "http://isin.twse.com.tw/isin/C_public.jsp?strMode=2", # 上市
                "otc": "http://isin.twse.com.tw/isin/C_public.jsp?strMode=4", # 上櫃
            }




        #class 底下的funtion 第一個parameter 會是自己 ， 一邊的funtion不會(不再class底下的funtion) 只有calss底下的會 
    def get_ticker(self, url):
        '''
        url: (data source)
            上市: https://isin.twse.com.tw/isin/C_public.jsp?strMode=2
            上櫃: https://isin.twse.com.tw/isin/C_public.jsp?strMode=4
        '''


        # 獲取資料
        response = requests.get(url)


        # 抓取一般股票
        dataframe = pd.read_html(response.text)[0]
        # 設定列標題為第一行的內容
        dataframe.columns = dataframe.iloc[0]
         # 篩選出CFICode為'ESVUFR'的股票
        dataframe = dataframe.query("CFICode == 'ESVUFR'")
         # 重新設定索引
        dataframe = dataframe.reset_index(drop = True)
        # 只保留特定列
        dataframe = dataframe[["有價證券代號及名稱", "市場別", "產業別"]]


        # 代號、名稱分割
        symbol, name = [], []
        for i in range(len(dataframe)):
            comp = dataframe["有價證券代號及名稱"][i].split("\u3000")
            if len(comp) != 2:
                comp = dataframe["有價證券代號及名稱"][i].split(" ")

            symbol.append(comp[0])
            name.append(comp[1])
        dataframe["symbol"], dataframe["name"] = symbol, name

        dataframe = dataframe.drop("有價證券代號及名稱", axis = 1)
        dataframe = dataframe.rename(columns = {"市場別": "market", "產業別": "industry"})


        return dataframe



    def check_mode(self, mode = "all"):
        mode_type = ["all", "listed", "otc", "other"]
        if mode not in mode_type:
            print("* Error * - mode can only be all/listed/otc/other")
            return True

        return False



    def get_TW_tickers(self, mode = "all"):
        '''
        mode (default = "all"):
            all:    上市 & 上櫃
            listed: 上市
            otc:    上櫃
        '''

        # 檢查輸入是否有誤
        mode_flag = self.check_mode(mode)
        if mode_flag:
            return


        # 取得指定市場的ticker
        if mode == "all":
            df_list = self.get_ticker(url = self.urls["listed"])
            df_otc = self.get_ticker(url = self.urls["otc"])
            tickers = pd.concat([df_list, df_otc], ignore_index = True)# 合併表格
        else:
            tickers = self.get_ticker(url = self.urls[mode])
        

        return tickers


    #給參數初始數值
    def get_price(self, start = "2022-01-01", end = "2022-01-31", mode = "all", query = None):
        # data source: yahoo finance
        '''
        start (default = "2021-01-01"):
            YYYY-MM-DD
        end (default = "2022-01-31"):
            YYYY-MM-DD
        mode (default = "all"):
            all:    上市 & 上櫃
            listed: 上市
            otc:    上櫃
            other:  自行輸入query
        query (default = None):
            mode為all、listed、otc: None
            mode為other: 
                        一檔股票的query: 上市: "2330.TW" 、 上櫃: "6510.TWO" 
                        多檔股票的query: "2330.TW 6510.TWO"
        '''
        

        # 檢查輸入是否有誤
        mode_flag = self.check_mode(mode)
        if mode_flag:
            return


        # 取得股票代號
        if mode != "other":
            print(f"{'-'*30} Get ticker. {'-'*30}")
            ticker = self.get_TW_tickers(mode)
        
            # 產生yfinance的query格式 (一次獲取多檔股票資料)，為了符合 Yahoo Finance 上台灣上市股票的命名慣例，使其可以被 yfinance 函數正確識別和下載
            query1 = ticker.query("market == '上市'")
            query1 = query1["symbol"].apply(lambda X: X + ".TW")

            query2 = ticker.query("market == '上櫃'")
            query2 = query2["symbol"].apply(lambda X: X + ".TWO")

            query1_2 = list(query1) + list(query2)
            query = str()
            for i in query1_2:
                query = query + i + " "


        # 獲取股價資料
        print(f"{'-'*30} Get price. {'-'*30}")
        query = query
        df = yf.download(query, start = start, end = end, group_by = 'ticker')


        # 資料整理及清洗
        print(f"{'-'*30} Clean data. {'-'*30}")
        price = pd.DataFrame()
        for i in tqdm(range(0, df.shape[1], 6)):
            df1 = df.iloc[:, i:i+6]

            if df.shape[1] != 6:
                symbol = df1.columns.get_level_values(0)[0]
                column = df1.columns.get_level_values(1)
                df1.columns = column
            else:
                symbol = query

            df1["Symbol"] = symbol#.replace(".TWO", "").replace(".TW", "")

            df1 = df1.dropna()
            df1 = df1.sort_values("Date")
            df1 = df1.reset_index()
            price = pd.concat([price, df1], ignore_index = True)
        price = price[["Symbol", "Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]].round(2)
        

        return price
    


   