from typing import Dict, List

import requests
import datetime


def fetch_rates_to_pln_nbp(start_date: datetime, end_date: datetime, currency="EUR") -> List[Dict]:
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    url = f"http://api.nbp.pl/api/exchangerates/rates/a/{currency.lower()}/{start_str}/{end_str}/"
    req = requests.get(url)
    rates = req.json()["rates"]
    rates = [{'date': r['effectiveDate'], 'rate': r['mid']} for r in rates]
    return rates
