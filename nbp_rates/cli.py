import argparse
from typing import Tuple

import arrow
from simple_term_menu import TerminalMenu

from nbp_rates.rates import fetch_rates_to_pln_nbp


def select_period_shell(last_months=12) -> Tuple[arrow.Arrow, arrow.Arrow]:
    options = [
        arrow.now().shift(months=-month_shift).format("YYYY-MM")
        for month_shift in range(last_months)
    ]
    selected_period = options[0]
    if last_months > 1:
        menu_entry_index = TerminalMenu(options).show()
        selected_period = options[menu_entry_index]

    start_date = arrow.get(selected_period).replace(day=1)
    end_date = start_date.shift(months=1, days=-1)
    return start_date, end_date


def main():
    parser = argparse.ArgumentParser(
        description="Generate work log based on gitlab actions annotated with issue link."
    )
    parser.add_argument(
        "--select-period",
        default=1,
        type=int,
        help="prompt with X last periods to select, default: 1",
    )
    parser.add_argument(
        "--currency",
        default="EUR",
        help="currency to PLN",
    )
    parser.add_argument(
        "--now",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="fetch latest rate",
    )
    parser.add_argument(
        "--best-exchange",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="fetch best exchange rate",
    )
    parser.add_argument(
        "--backend",
        default="revolut",
        help="backend to fetch rates example: nbp, walutomat, revolut",
    )
    parser.add_argument(
        "--start",
        default=None,
        help="start period example: 2022-07-01",
    )
    parser.add_argument(
        "--end",
        default=None,
        help="end period example: 2022-07-31",
    )
    parser.add_argument(
        "--predict",
        default=None,
        help="pass model example: ML, moving_average",
    )
    parser.add_argument(
        "--graph",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="show graph",
    )
    args = parser.parse_args()

    if args.start:
        start_date, end_date = arrow.get(args.start), arrow.get(args.end or arrow.now())
    else:
        start_date, end_date = select_period_shell(last_months=args.select_period)
    if end_date > arrow.now():
        end_date = arrow.now()

    if args.predict:
        from nbp_rates.predict import predict
        rates = predict(
            start_date=start_date,
            end_date=end_date,
            currency=args.currency,
            model=args.predict,
        )
        print(rates)
        return

    if args.graph:
        from nbp_rates.graph import show_rates_to_pln_graph
        show_rates_to_pln_graph(
            start_date=start_date,
            end_date=end_date,
            currency=args.currency,
        )
        return

    if args.now:
        from nbp_rates.rates import fetch_current_rates
        rates = fetch_current_rates(currency=args.currency, backend=args.backend)
        for k, v in rates.items():
            print(f"{k}\t\t{v}")
        return

    if args.best_exchange:
        from nbp_rates.rates import fetch_best_exchange_rates
        rates = fetch_best_exchange_rates()
        for backend, r in rates.items():
            if r['is_max']:
                print(f"{backend}\t\t{r['rate']}\t<--MAX")
            else:
                print(f"{backend}\t\t{r['rate']}")
        max_rate = max([r['rate'] for r in rates.values()])
        min_rate = min([r['rate'] for r in rates.values()])
        diff_max_min = max_rate - min_rate
        print(f"Diff 10 000 EUR -> PLN: {diff_max_min * 10000:.2f} PLN")
        print(f"Diff 20 000 EUR -> PLN: {diff_max_min * 20000:.2f} PLN")
        print(f"Diff 50 000 EUR -> PLN: {diff_max_min * 50000:.2f} PLN")
        print(f"Diff 100 000 EUR -> PLN: {diff_max_min * 100000:.2f} PLN")
        print(f"Diff 200 000 EUR -> PLN: {diff_max_min * 200000:.2f} PLN")
        print(f"Diff 300 000 EUR -> PLN: {diff_max_min * 300000:.2f} PLN")
        return

    rates = fetch_rates_to_pln_nbp(
        start_date=start_date,
        end_date=end_date,
        currency=args.currency,
    )
    for r in rates:
        if r['is_min']:
            print(f"{r['date']}\t{r['rate']}\t<--MIN")
        elif r['is_max']:
            print(f"{r['date']}\t{r['rate']}\t<--MAX")
        else:
            print(f"{r['date']}\t{r['rate']}")


if __name__ == '__main__':
    main()
