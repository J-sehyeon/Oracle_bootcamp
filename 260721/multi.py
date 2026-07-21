import multiprocessing
import requests 
import io 
import pandas as pd
import time 

def get_data(page):
    url = "https://finance.naver.com/marketindex/worldDailyQuote.naver?marketindexCd=OIL_DU&fdtc=2&page={}"
    return pd.read_html(io.StringIO(requests.get(url.format(page)).text))[0]


if __name__ == "__main__":
    target_number = range(200,300)

    start_time = time.perf_counter()

    with multiprocessing.Pool(processes=10) as pool:
        results = pool.map(get_data, target_number)

    end_time = time.perf_counter()
    print(f"{end_time - start_time}초")
    pd.concat(results).to_csv("./multi.csv", index=False, encoding='utf-8-sig')
