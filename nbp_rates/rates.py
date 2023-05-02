from typing import Dict, List

import requests
import datetime


def fetch_latest_rates_walutomat(currency="EUR") -> dict:
    url = f"https://user.walutomat.pl/api/public/marketBrief/{currency.upper()}_PLN"
    req = requests.get(url)
    try:
        rates = req.json()["bestOffers"]
    except requests.exceptions.JSONDecodeError:
        raise ValueError(f"Walutomat returned invalid JSON: {req.text}")
    return rates


def fetch_latest_rates_revolut(currency="EUR") -> dict:
    url = f"https://www.revolut.com/api/exchange/quote?amount=1000&country=US&fromCurrency={currency.upper()}&isRecipientAmount=false&toCurrency=PLN"
    req = requests.get(url, headers={"accept-language": "en-US,en;q=0.9,pl;q=0.8"})
    try:
        rates = req.json()['rate']
    except requests.exceptions.JSONDecodeError:
        raise ValueError(f"Revolut returned invalid JSON: {req.text}")
    return rates


def fetch_current_rates(currency="EUR", backend="revolut") -> dict:
    if backend == "revolut":
        return fetch_latest_rates_revolut(currency)
    elif backend == "walutomat":
        return fetch_latest_rates_walutomat(currency)
    else:
        raise ValueError(f"Unknown backend: {backend}")


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
