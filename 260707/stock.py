import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import csv

# --name 005930 --sdate 2060101 --edate 20260707
# python3 stock.py --name 005930 --sdate 20260406 --edate 20260706


def main(name, sdate, edate):
    url = f'https://m.stock.naver.com/front-api/external/chart/domestic/info?symbol={name}&requestType=1&startTime={sdate}&endTime={edate}&timeframe=day'
    r = requests.get(url)
    stock_list = eval(r.text.strip())
    with open(f'./{name}.csv', 'w', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerows(stock_list)





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name')
    parser.add_argument('--sdate')
    parser.add_argument('--edate')
    args = parser.parse_args()

    main(args.name, args.sdate, args.edate)
