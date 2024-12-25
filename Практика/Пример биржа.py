import pandas as pd
import requests
from urllib import parse
from datetime import datetime, timedelta

pd.set_option("display.max_columns", 15)

def query(method: str, **kwargs):
    """
    Отправляет запрос к ISS MOEX API
    """
    try:
        url = f"https://iss.moex.com/iss/{method}.json"
        if kwargs:
            url += "?" + parse.urlencode(kwargs)
        response = requests.get(url)
        response.encoding = 'utf-8'
        return response.json()
    except Exception as e:
        print(f"Query error: {str(e)}")
        return None


def flatten(data: dict, blockname: str):
    """
    Преобразует JSON ответ в удобный для pandas формат
    """
    return [{k: r[i] for i, k in enumerate(data[blockname]['columns'])} for r in data[blockname]['data']]


def get_candles(ticker: str, engine: str, market: str, from_date: str, till_date: str, interval: int = 1):
    """
    Получает свечи по тикеру за указанный период времени и временной промежуток
    """
    method = f"engines/{engine}/markets/{market}/securities/{ticker}/candles"
    params = {
        'from': from_date,
        'till': till_date,
        'interval': 1,  # Интервал 1 минута
        'start': 0
    }
    data = query(method, **params)
    if data:
        candles = flatten(data, 'candles')
        # Добавляем столбец с названием тикера
        for candle in candles:
            candle['ticker'] = ticker
        return candles
    return []


def save_to_csv(data, filename="moex_data2.csv"):
    """
    Сохраняет данные в CSV
    """
    df = pd.DataFrame(data)
    df.to_csv(filename, mode='a', header=not pd.io.common.file_exists(filename), index=False)

def main():
    tickers = ['POSI', 'SMLT','ENPG','GMKN','IMOEX','TCSG','TRNFP','KMEZ','BELU','BSPBP']  # Список тикеров
    engine = "stock"
    market = "shares"

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 6, 30)

    all_data = []

    while start_date <= end_date:
        date_str = start_date.strftime("%Y-%m-%d")
        next_day = start_date + timedelta(days=1)

        for ticker in tickers:
            print(f"Получаем данные по тикеру {ticker} на дату {date_str}...")

            # Период с 09:00 до 18:00
            candles_data_morning = get_candles(ticker, engine, market, from_date=f"{date_str} 09:00:00",
                                               till_date=f"{date_str} 18:00:00")
            all_data.extend(candles_data_morning)

            # Период с 18:01 до 23:59
            candles_data_evening = get_candles(ticker, engine, market, from_date=f"{date_str} 18:01:00",
                                               till_date=f"{date_str} 23:59:00")
            all_data.extend(candles_data_evening)

        # Переход к следующему дню
        start_date = next_day

    # Сохраняем все данные в CSV
    save_to_csv(all_data)


if __name__ == '__main__':
    main()
