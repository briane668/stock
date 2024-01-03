https://hackmd.io/8_IH5lGwQz6gQCACmTiKOg

# Stock

* Get stock ticker  `獲得股票代號及產業`
* Get stock price `獲得歷史股價`
* Get financial statement `獲得財務報表`
* Get chip data `獲得三大法人`
* Get spread of shareholding `獲得股權分散表`



## Get stock ticker.


```python=
import stock_data as stock

scrapy = stock.Scrapy()
df = scrapy.get_TW_tickers(mode = "all")
df
```


### Parameters
    mode (default = "all"):
        all:    上市 & 上櫃
        listed: 上市
        otc:    上櫃


## Get stock price.


**指定股票代號**

```python=
import stock_data as stock

scrapy = stock.Scrapy()
df = scrapy.get_price(
    start  = "2022-01-01",
    end = "2022-01-31",
    mode = "other",
    query = "2330.TW"
)
df
```
