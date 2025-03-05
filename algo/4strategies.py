import yfinance as yf
import pandas as pd
import numpy as np
import math
# === Insert Indicator and Strategy Code Here ===
# (Paste the entire integrated code provided earlier)
# === Indicator Calculation Functions ===

def calculate_rsi(prices_df: pd.DataFrame, period: int = 14) -> pd.Series:
    delta = prices_df["close"].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger_bands(prices_df: pd.DataFrame, window: int = 20) -> tuple[pd.Series, pd.Series]:
    sma = prices_df["close"].rolling(window).mean()
    std_dev = prices_df["close"].rolling(window).std()
    upper_band = sma + (std_dev * 2)
    lower_band = sma - (std_dev * 2)
    return upper_band, lower_band

def calculate_ema(prices_df: pd.DataFrame, window: int) -> pd.Series:
    return prices_df["close"].ewm(span=window, adjust=False).mean()

def calculate_adx(prices_df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    prices_df["high_low"] = prices_df["high"] - prices_df["low"]
    prices_df["high_close"] = abs(prices_df["high"] - prices_df["close"].shift())
    prices_df["low_close"] = abs(prices_df["low"] - prices_df["close"].shift())
    prices_df["tr"] = prices_df[["high_low", "high_close", "low_close"]].max(axis=1)

    prices_df["up_move"] = prices_df["high"] - prices_df["high"].shift()
    prices_df["down_move"] = prices_df["low"].shift() - prices_df["low"]

    prices_df["plus_dm"] = np.where((prices_df["up_move"] > prices_df["down_move"]) & (prices_df["up_move"] > 0), prices_df["up_move"], 0)
    prices_df["minus_dm"] = np.where((prices_df["down_move"] > prices_df["up_move"]) & (prices_df["down_move"] > 0), prices_df["down_move"], 0)

    prices_df["+di"] = 100 * (prices_df["plus_dm"].ewm(span=period).mean() / prices_df["tr"].ewm(span=period).mean())
    prices_df["-di"] = 100 * (prices_df["minus_dm"].ewm(span=period).mean() / prices_df["tr"].ewm(span=period).mean())
    prices_df["dx"] = 100 * abs(prices_df["+di"] - prices_df["-di"]) / (prices_df["+di"] + prices_df["-di"])
    prices_df["adx"] = prices_df["dx"].ewm(span=period).mean()

    return prices_df[["adx", "+di", "-di"]]

def calculate_atr(prices_df, window=14):
    """
    Calculate the Average True Range (ATR).
    """
    high_low = prices_df["high"] - prices_df["low"]
    high_close = abs(prices_df["high"] - prices_df["close"].shift(1))
    low_close = abs(prices_df["low"] - prices_df["close"].shift(1))

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window).mean()
    return atr

# === Strategy Functions ===
def calculate_trend_signals(prices_df):
    """
    Advanced trend following strategy using multiple timeframes and indicators
    """
    # Calculate EMAs for multiple timeframes
    ema_8 = calculate_ema(prices_df, 8)
    ema_21 = calculate_ema(prices_df, 21)
    ema_55 = calculate_ema(prices_df, 55)

    # Calculate ADX for trend strength
    adx = calculate_adx(prices_df, 14)

    # Determine trend direction and strength
    short_trend = (ema_8 > ema_21)
    medium_trend = (ema_21 > ema_55)

    # Extract scalar values for the latest trends
    short_trend_last = short_trend.iloc[-1].item()
    medium_trend_last = medium_trend.iloc[-1].item()
    

    # Combine signals with confidence weighting
    trend_strength = adx["adx"].iloc[-1] / 100.0

    if short_trend_last and medium_trend_last:
        signal = "bullish"
        confidence = trend_strength
    elif not short_trend_last and not medium_trend_last:
        signal = "bearish"
        confidence = trend_strength
    else:
        signal = "neutral"
        confidence = 0.5

    return {
        "signal": signal,
        "confidence": confidence,
        "metrics": {
            "adx": float(adx["adx"].iloc[-1]),
            "trend_strength": float(trend_strength),
        },
    }
def calculate_mean_reversion_signals(prices_df):
    """
    Mean reversion strategy using statistical measures and Bollinger Bands
    """
    # Calculate z-score of price relative to moving average
    ma_50 = prices_df["close"].rolling(window=50).mean()
    std_50 = prices_df["close"].rolling(window=50).std()
    z_score = (prices_df["close"] - ma_50) / std_50

    # Calculate Bollinger Bands
    bb_upper, bb_lower = calculate_bollinger_bands(prices_df)

    # Calculate RSI with multiple timeframes
    rsi_14 = calculate_rsi(prices_df, 14)
    rsi_28 = calculate_rsi(prices_df, 28)

    # Extract the last scalar values
    z_score_last = z_score.iloc[-1] if isinstance(z_score.iloc[-1], (int, float)) else z_score.iloc[-1].item()
    price_vs_bb_last = ((prices_df["close"].iloc[-1] - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1]))
    rsi_14_last = rsi_14.iloc[-1]
    rsi_28_last = rsi_28.iloc[-1]

    # Mean reversion signals
    if z_score_last < -2 and price_vs_bb_last < 0.2:
        signal = "bullish"
        confidence = min(abs(z_score_last) / 4, 1.0)
    elif z_score_last > 2 and price_vs_bb_last > 0.8:
        signal = "bearish"
        confidence = min(abs(z_score_last) / 4, 1.0)
    else:
        signal = "neutral"
        confidence = 0.5

    return {
        "signal": signal,
        "confidence": confidence * 100,  # Representing in percentage
        "metrics": {
            "z_score": round(z_score_last, 2),
            "price_vs_bb": round(price_vs_bb_last, 2),
            "rsi_14": round(rsi_14_last, 2),
            "rsi_28": round(rsi_28_last, 2),
        },
    }
def calculate_momentum_signals(prices_df):
    """
    Multi-factor momentum strategy
    """
    # Price momentum
    returns = prices_df["close"].pct_change()
    mom_1m = returns.rolling(21).sum()
    mom_3m = returns.rolling(63).sum()
    mom_6m = returns.rolling(126).sum()

    # Volume momentum
    volume_ma = prices_df["volume"].rolling(21).mean()
    volume_momentum = prices_df["volume"] / volume_ma

    # Handle missing or ambiguous values for price momentum
    mom_1m_last = mom_1m.iloc[-1] if not mom_1m.iloc[-1].isna().any() else 0.0
    mom_3m_last = mom_3m.iloc[-1] if not mom_3m.iloc[-1].isna().any() else 0.0
    mom_6m_last = mom_6m.iloc[-1] if not mom_6m.iloc[-1].isna().any() else 0.0

    # Ensure scalar extraction for price momentum
    if isinstance(mom_1m_last, pd.Series):
        mom_1m_last = mom_1m_last.values[0]
    if isinstance(mom_3m_last, pd.Series):
        mom_3m_last = mom_3m_last.values[0]
    if isinstance(mom_6m_last, pd.Series):
        mom_6m_last = mom_6m_last.values[0]

    # Handle missing or ambiguous values for volume momentum
    volume_momentum_last = volume_momentum.iloc[-1] if not volume_momentum.iloc[-1].isna().any() else 0.0

    # Ensure scalar extraction for volume momentum
    if isinstance(volume_momentum_last, pd.Series):
        volume_momentum_last = volume_momentum_last.values[0]

    # Calculate momentum score
    momentum_score = (0.4 * mom_1m_last + 0.3 * mom_3m_last + 0.3 * mom_6m_last)

    # Volume confirmation
    volume_confirmation = volume_momentum_last > 1.0

    if momentum_score > 0.05 and volume_confirmation:
        signal = "bullish"
        confidence = min(abs(momentum_score) * 5, 1.0)
    elif momentum_score < -0.05 and volume_confirmation:
        signal = "bearish"
        confidence = min(abs(momentum_score) * 5, 1.0)
    else:
        signal = "neutral"
        confidence = 0.5

    return {
        "signal": signal,
        "confidence": confidence * 100,  # Representing in percentage
        "metrics": {
            "momentum_1m": round(mom_1m_last, 4),
            "momentum_3m": round(mom_3m_last, 4),
            "momentum_6m": round(mom_6m_last, 4),
            "volume_momentum": round(volume_momentum_last, 4),
        },
    }


def calculate_volatility_signal(prices_df):
    """
    Volatility-based trading strategy.
    """
    # Calculate percentage change for historical volatility
    returns = prices_df["close"].pct_change()

    # Historical volatility
    hist_vol = returns.rolling(21).std() * math.sqrt(252)

    # Volatility regime detection
    vol_ma = hist_vol.rolling(63).mean()
    vol_regime = hist_vol / vol_ma

    # Volatility mean reversion
    vol_z_score = (hist_vol - vol_ma) / hist_vol.rolling(63).std()

    # ATR ratio
    close = prices_df["close"]
    atr = calculate_atr(prices_df)
    close=close.squeeze()
    atr=atr.squeeze()

    # Ensure 'close' and 'atr' are properly aligned and handle scalars
    close_last = close.iloc[-1].item() if not pd.isna(close.iloc[-1]) else 0.0
    atr_last = atr.iloc[-1].item() if not pd.isna(atr.iloc[-1]) else 0.0

    # Calculate ATR ratio safely
    atr_ratio = atr_last / close_last if close_last != 0 else 0.0

    # Generate signal based on volatility regime
    current_vol_regime = vol_regime.iloc[-1]
    # Extract the last value and ensure it's a scalar
    current_vol_regime = float(vol_regime.iloc[-1])

    vol_z = float(vol_z_score.iloc[-1])
    
    if current_vol_regime < 0.8 and vol_z < -1:
        signal = "bullish"  # Low vol regime, potential for expansion
        confidence = min(abs(vol_z) / 3, 1.0)
    elif current_vol_regime > 1.2 and vol_z > 1:
        signal = "bearish"  # High vol regime, potential for contraction
        confidence = min(abs(vol_z) / 3, 1.0)
    else:
        signal = "neutral"
        confidence = 0.5

    return {
        "signal": signal,
        "confidence": confidence,
        "metrics": {
            "historical_volatility": float(hist_vol.iloc[-1]),
            "volatility_regime": float(current_vol_regime),
            "volatility_z_score": float(vol_z),
            "atr_ratio": float(atr_ratio),
        },
    }


# === Fetch Data for RELIANCE.NS ===
def fetch_stock_data(ticker: str, start_date: str, end_date: str, interval: str = "1d") -> pd.DataFrame:
    prices_df = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    prices_df = prices_df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
    return prices_df

# === Main Script ===
if __name__ == "__main__":
    # Fetch RELIANCE.NS data
    ticker = "RELIANCE.NS"
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    prices_df = fetch_stock_data(ticker, start_date, end_date)
    
    if not prices_df.empty:
        # Calculate Trend Following Signals
        trend_signals = calculate_trend_signals(prices_df)
        print("Trend Following Signals:", trend_signals)
        
        # Calculate Mean Reversion Signals
        mean_reversion_signals = calculate_mean_reversion_signals(prices_df)
        print("Mean Reversion Signals:", mean_reversion_signals)
        
        #calculate momentum signals 
        momentum_signals=calculate_momentum_signals(prices_df)
        print("Momentum signals:", momentum_signals)\
    
        #calculate volatility signals 
        volatility_signals=calculate_volatility_signal(prices_df)
        print("Volatility signals:", volatility_signals)
    else:
        print(f"No data found for {ticker} in the specified date range.")
