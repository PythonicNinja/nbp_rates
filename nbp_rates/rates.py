from typing import Dict, List

import requests
import datetime


def fetch_latest_rates_forex(currency="EUR") -> dict:
    url = f"https://user.walutomat.pl/api/public/marketBrief/{currency.upper()}_PLN"
    req = requests.get(url)
    try:
        rates = req.json()["bestOffers"]
    except requests.exceptions.JSONDecodeError:
        raise ValueError(f"Walutomat returned invalid JSON: {req.text}")
    return rates


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
