from enum import Enum
from typing import Dict, List

import requests
import datetime


class Backends(Enum):
    REVOLUT = "revolut"
    WALUTOMAT = "walutomat"


def fetch_latest_rates_walutomat(currency="EUR") -> dict:
    url = f"https://user.walutomat.pl/api/public/marketEstimate/sell/10000/{currency.upper()}/PLN"
    req = requests.get(url)
    try:
        rates = req.json()["exchange_offers"][0]
    except requests.exceptions.JSONDecodeError:
        raise ValueError(f"Walutomat returned invalid JSON: {req.text}")
    return rates


def fetch_latest_rates_revolut(currency="EUR") -> dict:
    url = f"https://www.revolut.com/api/exchange/quote?amount=1000&country=US&fromCurrency={currency.upper()}&isRecipientAmount=false&toCurrency=PLN"
    req = requests.get(url, headers={"accept-language": "en-US,en;q=0.9,pl;q=0.8"})
    try:
        rates = req.json()["rate"]
    except requests.exceptions.JSONDecodeError:
        raise ValueError(f"Revolut returned invalid JSON: {req.text}")
    return rates


def fetch_current_rates(
    currency="EUR", backend: Backends = Backends.REVOLUT.value
) -> dict:
    if backend == Backends.REVOLUT.value:
        return fetch_latest_rates_revolut(currency)
    elif backend == Backends.WALUTOMAT.value:
        return fetch_latest_rates_walutomat(currency)
    else:
        raise ValueError(f"Unknown backend: {backend}")


def fetch_best_exchange_rates(currency="EUR") -> dict:
    rates = {}
    for backend in Backends:
        try:
            rate = fetch_current_rates(currency, backend.value)
            if backend == Backends.WALUTOMAT:
                rate["rate"] = (
                    float(rate.get("display_amount", "0").replace(",", ".")) / 10000
                )
            else:
                rate["rate"] = float(rate.get("rate") or rate.get("bid_now"))
            rates[backend.value] = rate
        except ValueError:
            continue
    rate_values = [r["rate"] for r in rates.values()]
    min_rate = min(rate_values)
    max_rate = max(rate_values)
    for _, r in rates.items():
        r["is_min"] = r["rate"] == min_rate
        r["is_max"] = r["rate"] == max_rate
    return rates


def fetch_rates_to_pln_nbp(
    start_date: datetime, end_date: datetime, currency="EUR"
) -> List[Dict]:
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    url = f"http://api.nbp.pl/api/exchangerates/rates/a/{currency.lower()}/{start_str}/{end_str}/"
    req = requests.get(url)
    try:
        rates = req.json()["rates"]
    except requests.exceptions.JSONDecodeError:
        raise ValueError(f"NBP API returned invalid JSON: {req.text}")
    rates = [{"date": r["effectiveDate"], "rate": r["mid"]} for r in rates]
    min_rate = min(r["rate"] for r in rates)
    max_rate = max(r["rate"] for r in rates)
    for r in rates:
        r["is_min"] = r["rate"] == min_rate
        r["is_max"] = r["rate"] == max_rate
    return rates
