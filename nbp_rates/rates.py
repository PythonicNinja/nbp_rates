from typing import Dict, List

import requests
import datetime


def fetch_rates_to_pln_nbp(start_date: datetime, end_date: datetime, currency="EUR") -> List[Dict]:
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    url = f"http://api.nbp.pl/api/exchangerates/rates/a/{currency.lower()}/{start_str}/{end_str}/"
    req = requests.get(url)
    try:
        rates = req.json()["rates"]
    except requests.exceptions.JSONDecodeError:
        raise ValueError(f"NBP API returned invalid JSON: {req.text}")
    rates = [{'date': r['effectiveDate'], 'rate': r['mid']} for r in rates]
    min_rate = min(r['rate'] for r in rates)
    max_rate = max(r['rate'] for r in rates)
    for r in rates:
        r['is_min'] = r['rate'] == min_rate
        r['is_max'] = r['rate'] == max_rate
    return rates


def moving_avg(rates: List[Dict], n=3):
    for i in range(len(rates)):
        if i < n:
            continue
        avg = sum(r['rate'] for r in rates[i-n:i]) / n
        rates[i][f"avg_{n}"] = avg
    return rates


def predict_price_for_period(start_date: datetime, end_date: datetime, currency="EUR"):
    rates = fetch_rates_to_pln_nbp(start_date, end_date, currency)
    rates = moving_avg(rates, n=3)
    rates = moving_avg(rates, n=7)
    rates = moving_avg(rates, n=14)
    rates = moving_avg(rates, n=30)
    rates = moving_avg(rates, n=90)
    rates = moving_avg(rates, n=180)
    rates = moving_avg(rates, n=360)
    return {k: v for k, v in rates[-1].items() if k.startswith("avg_")}


if __name__ == '__main__':
    moving_averages = predict_price_for_period(datetime.datetime(2022, 3, 20), datetime.datetime(2023, 3, 20))
    print(moving_averages)
