from typing import Dict, List

import arrow as arrow
import requests
import datetime
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor


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
        avg = sum(r['rate'] for r in rates[i - n:i]) / n
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


def predict_price_for_period_using_different_ml_models(
        start_date: datetime, end_date: datetime, currency="EUR"
) -> dict:
    rates = fetch_rates_to_pln_nbp(start_date, end_date, currency)
    rates = [r['rate'] for r in rates]
    lr = LinearRegression()
    svm = SVR(kernel='rbf', C=1e3, gamma=0.1)
    dt = DecisionTreeRegressor()
    rf = RandomForestRegressor()
    X = np.array(rates).reshape(-1, 1)
    y = np.array(rates).reshape(-1, 1)
    lr.fit(X, y)
    svm.fit(X, y)
    dt.fit(X, y)
    rf.fit(X, y.ravel())
    return {
        "linear_regression": lr.predict(np.array([rates[-1]]).reshape(-1, 1))[0][0],
        "svm": svm.predict(np.array([rates[-1]]).reshape(-1, 1))[-1],
        "decision_tree": dt.predict(np.array([rates[-1]]).reshape(-1, 1))[-1],
        "random_forest": rf.predict(np.array([rates[-1]]).reshape(-1, 1))[-1],
    }


if __name__ == '__main__':
    last_days_predictions = (
        365, 180, 90, 30, 14, 7, 3
    )

    for last_days in last_days_predictions:
        end = arrow.now().datetime
        start = end - datetime.timedelta(days=last_days)

        moving_averages = predict_price_for_period(start_date=start, end_date=end)
        prices = predict_price_for_period_using_different_ml_models(start_date=start, end_date=end)

        # for k, v in moving_averages.items():
        #     print(f"{k}: {v}")
        # print()
        # for k, v in prices.items():
        #     print(f"{k}: {v}")

        avg_price = sum(prices.values()) / len(prices)
        print(f"ML avg_price: {avg_price}")
