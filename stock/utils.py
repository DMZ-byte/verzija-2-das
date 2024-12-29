import pandas as pd
from ta.momentum import RSIIndicator, StochasticOscillator, ROCIndicator
from ta.trend import SMAIndicator,MACD, EMAIndicator, WMAIndicator, CCIIndicator, ADXIndicator


def calculate_indicators(data):
    # Moving averages
    data['SMA'] = SMAIndicator(data['last_transaction_price'], window=7).sma_indicator()
    data['EMA'] = EMAIndicator(data['last_transaction_price'], window=7).ema_indicator()
    data['WMA'] = WMAIndicator(data['last_transaction_price'], window=7).wma()
    data['TEMA'] = EMAIndicator(data['EMA'], window=3).ema_indicator()
    data['MACD'] = MACD(data['last_transaction_price']).macd()
    # Oscillators
    data['RSI'] = RSIIndicator(data['last_transaction_price'], window=14).rsi()

    data['Stochastic_K'] = StochasticOscillator(
        high = data['max_price'],
        low=data['min_price'],
        close= data['last_transaction_price'],
        window=14, smooth_window=3
    ).stoch()
    data['CCI'] = CCIIndicator(
        high=data['max_price'],
        low=data['min_price'],
        close=data['last_transaction_price'],
        window=14
    ).cci()
    data['ADX'] = ADXIndicator(
        high=data['max_price'],
        low=data['min_price'],
        close=data['last_transaction_price'],
        window=14
    ).adx()
    data['ROC'] = ROCIndicator(data['last_transaction_price'], window=14).roc()
    return data


def generate_signals(data):
    data['Signal'] = 'Hold'
    data.loc[data['RSI'] < 30, 'Signal'] = 'Buy'
    data.loc[data['RSI'] > 70, 'Signal'] = 'Sell'
    return data


def determine_signals(data):
    # RSI Buy/Sell Signal
    data['RSI_signal'] = data['RSI'].apply(lambda x: 'Buy' if x < 30 else 'Sell' if x > 70 else 'Neutral')

    # Stochastic Oscillator Buy/Sell Signal
    data['Stochastic_K_signal'] = data['Stochastic_K'].apply(
        lambda x: 'Buy' if x < 20 else 'Sell' if x > 80 else 'Neutral')

    # Commodity Channel Index (CCI) Buy/Sell Signal
    data['CCI_signal'] = data['CCI'].apply(lambda x: 'Buy' if x < -100 else 'Sell' if x > 100 else 'Neutral')

    # Average Directional Index (ADX) Buy/Sell Signal
    data['ADX_signal'] = data['ADX'].apply(lambda x: 'Buy' if x > 25 else 'Neutral')

    # Rate of Change (ROC) Buy/Sell Signal
    data['ROC_signal'] = data['ROC'].apply(lambda x: 'Buy' if x > 0 else 'Sell' if x < 0 else 'Neutral')

    # Moving Averages Signals (Crossover Example)
    data['SMA_signal'] = data['last_transaction_price'] > data['SMA']
    data['EMA_signal'] = data['last_transaction_price'] > data['EMA']
    data['WMA_signal'] = data['last_transaction_price'] > data['WMA']
    data['TEMA_signal'] = data['last_transaction_price'] > data['TEMA']
    data['MACD_signal'] = data['last_transaction_price'] > data['MACD']

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
