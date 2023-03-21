import datetime
from typing import Dict, List

import arrow as arrow
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from nbp_rates.rates import fetch_rates_to_pln_nbp


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
    svm.fit(X, y.squeeze())
    dt.fit(X, y)
    rf.fit(X, y.squeeze())

    current = np.array(rates).reshape(-1, 1)

    linear_regression = lr.predict(current)
    svm_prediction = svm.predict(current)
    decision_tree = dt.predict(current)
    random_forest = rf.predict(current)

    predictions = {
        "linear_regression": linear_regression[-1][0],
        "svm": svm_prediction[-1],
        "decision_tree": decision_tree[-1],
        "random_forest": random_forest[-1],
    }
    predictions["avg"] = sum(predictions.values()) / len(predictions)
    return predictions


def predict(
    start_date: datetime, end_date: datetime, currency="EUR", model: str = "moving_average"
):
    model = model.lower()
    if model == "moving_average":
        return predict_price_for_period(start_date, end_date, currency)
    elif model == "ml":
        return predict_price_for_period_using_different_ml_models(start_date, end_date, currency)
    else:
        raise ValueError(f"Unknown model: {model}")


if __name__ == '__main__':
    last_days_predictions = (
        365, 180, 90, 30, 14, 7, 3
    )

    for last_days in last_days_predictions:
        end = arrow.now().datetime
        start = end - datetime.timedelta(days=last_days)

        moving_averages = predict_price_for_period(start_date=start, end_date=end)
        prices = predict_price_for_period_using_different_ml_models(start_date=start, end_date=end)