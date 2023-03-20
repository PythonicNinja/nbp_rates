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
        "--cache",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="If cache should be used for past dates",
    )
    args = parser.parse_args()

    if args.start:
        start_date, end_date = arrow.get(args.start), arrow.get(args.end or arrow.now())
    else:
        start_date, end_date = select_period_shell(last_months=args.select_period)
    if end_date > arrow.now():
        end_date = arrow.now()

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
