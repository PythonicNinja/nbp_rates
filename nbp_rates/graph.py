import pandas as pd
import matplotlib.pyplot as plt

from nbp_rates.rates import fetch_rates_to_pln_nbp


def show_graph(start_date, end_date, currency="EUR"):
    rates = fetch_rates_to_pln_nbp(
        start_date=start_date,
        end_date=end_date,
        currency=currency,
    )
    df = pd.DataFrame(rates)
    df['date'] = pd.to_datetime(df['date'])
    df['rate'] = pd.to_numeric(df['rate'])
    df['is_min'] = df['is_min'].astype(bool)
    df['is_max'] = df['is_max'].astype(bool)
    df = df.set_index('date')
    df['rate'].plot()
    plt.show()
