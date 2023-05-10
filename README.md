# nbp_rates

[![Python package](https://github.com/PythonicNinja/nbp_rates/actions/workflows/python-package.yml/badge.svg)](https://github.com/PythonicNinja/nbp_rates/actions/workflows/python-package.yml)

Utility for getting exchange rates from multiple backends.

Supported backends:
- Revolut
- Walutomat
- NBP (Narodowy Bank Polski)

## Installation

```bash
git clone git@github.com:PythonicNinja/nbp_rates.git
cd nbp_rates
pip install -e .
```

After that you will have `nbp_rates` command available in your shell.

## Fetcher

Fetcher is a default mode of this utility. It fetches exchange rates from NBP and prints them to stdout.

```python
| => nbp_rates --currency eur --select-period 12
2023-02-01	4.708
2023-02-02	4.7079
2023-02-03	4.692	<--MIN
2023-02-06	4.7195
2023-02-07	4.7476
2023-02-08	4.7402
2023-02-09	4.7363
2023-02-10	4.7716
2023-02-13	4.7895	<--MAX
2023-02-14	4.7847
2023-02-15	4.7593
2023-02-16	4.7728
2023-02-17	4.7747
2023-02-20	4.7542
2023-02-21	4.7469
2023-02-22	4.7538
2023-02-23	4.7525
2023-02-24	4.7245
2023-02-27	4.7162
2023-02-28	4.717
```

```python
| => nbp_rates
2023-03-01	4.6925
2023-03-02	4.675	<--MIN
2023-03-03	4.7046
2023-03-06	4.7073
2023-03-07	4.6871
2023-03-08	4.7018
2023-03-09	4.6836
2023-03-10	4.6838
2023-03-13	4.6848
2023-03-14	4.6909
2023-03-15	4.7015
2023-03-16	4.6978
2023-03-17	4.7062
2023-03-20	4.7109	<--MAX
```

With `--now` you can fetch current exchange rate.

```python
| => nbp_rates --currency eur --now
bid_now		4.7005
ask_now		4.7074
forex_now		4.707
bid_old		4.7003
ask_old		4.7074
forex_old		4.707
ask_trend		neutral
bid_trend		up
forex_trend		neutral
```

## Predictor

With option of `--predict` you can predict exchange rate for next day.
You can choose between `ml` and `moving_average` model.

`--predict ml` model uses machine learning algorithms to predict exchange rate. 

```python
| => nbp_rates --predict ml
{'linear_regression': 4.7109, 'svm': 4.69295, 'decision_tree': 4.7109, 'random_forest': 4.709264999999995, 'avg': 4.706003749999998}
```

`--predict moving_average` model uses simple arithmetic mean of exchange rates.
It will try to fit 3, 7, 14, 30, 90, 180, 300 days moving averages to given period.

```python
nbp_rates --currency eur --start=2022-12-01 --end=2023-03-31 --predict moving_average
{'avg_3': 4.701833333333333, 'avg_7': 4.692657142857143, 'avg_14': 4.695278571428572, 'avg_30': 4.72594}
```