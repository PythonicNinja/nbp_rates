from typing import Dict, List

import requests
import datetime


def fetch_eur_pln_nbp(start_date: datetime, end_date: datetime, currency="EUR") -> List[Dict]:
    """Fetch EUR/PLN exchange rates from NBP API."""
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    url = f"http://api.nbp.pl/api/exchangerates/rates/a/{currency.lower()}/{start_str}/{end_str}/"
    print(f"url {url}")
    req = requests.get(url)
    return req.json()
