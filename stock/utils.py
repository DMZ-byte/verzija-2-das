import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator


def calculate_indicators(data):
    data['SMA'] = SMAIndicator(data['last_transaction_price'], window=7).sma_indicator()
    data['EMA'] = EMAIndicator(data['last_transaction_price'], window=7).ema_indicator()
    data['RSI'] = RSIIndicator(data['last_transaction_price'], window=14).rsi()
    return data


def generate_signals(data):
    data['Signal'] = 'Hold'
    data.loc[data['RSI'] < 30, 'Signal'] = 'Buy'
    data.loc[data['RSI'] > 70, 'Signal'] = 'Sell'
    return data
def load_csv(file_path):
    return pd.read_csv(file_path, parse_dates=['Датум'])

def filter_data_by_period(data, period, company):
    """Filter data for a specific period and company."""
    if period == '1day':
        filtered = data[data['Датум'] == data['Датум'].max()]
    elif period == '1month':
        filtered = data[data['Датум'] >= data['Датум'].max() - pd.DateOffset(months=1)]
    elif period == '1year':
        filtered = data[data['Датум'] >= data['Датум'].max() - pd.DateOffset(years=1)]
    else:
        filtered = data
    return filtered[data['Company'] == company]

def normalize_numeric(value):
    if pd.isnull(value):  # Handle NaN or null values
        return None
    if isinstance(value, (int, float)):  # If already a number, return as is
        return value
    try:
        # Convert value to string, replace separators, and return as float
        return float(str(value).replace('.', '').replace(',', '.'))
    except ValueError:
        return None
