import yfinance as yf
import pandas as pd
import numpy as np
import math
import json
        
##### Placeholder Signal Calculation Functions #####
def calculate_rsi(prices_df: pd.DataFrame, period: int = 14) -> pd.Series:
    delta = prices_df["close"].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger_bands(prices_df: pd.DataFrame, window: int = 20) -> tuple[pd.Series, pd.Series]:
    sma = prices_df["close"].rolling(20).mean()
    std_dev = prices_df["close"].rolling(20).std()
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
    prices_df = yf.download(ticker, start_date, end=end_date, interval='1d')
    prices_df = prices_df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
    return prices_df

def weighted_signal_combination(signals, weights):
    """
    Combines multiple trading signals using a weighted approach.

    Args:
        signals (dict): A dictionary containing signals from various strategies in the form:
                        {strategy_name: {"signal": "neutral", "confidence": 0.5, "metrics": {...}}}
        weights (dict): A dictionary containing weights for each strategy.

    Returns:
        dict: A dictionary with the combined signal and its confidence score.
    """
    # Map signal strings to numeric values
    signal_values = {"bullish": 1, "neutral": 0, "bearish": -1}

    weighted_sum = 0
    total_confidence = 0

    for strategy, signal in signals.items():
        try:
            # Extract signal and confidence
            numeric_signal = signal_values[signal["signal"]]
            confidence = signal["confidence"]

            # Get the weight for the current strategy
            weight = weights.get(strategy, 0)

            # Accumulate weighted sum and total confidence
            weighted_sum += numeric_signal * weight * confidence
            total_confidence += weight * confidence
        except KeyError as e:
            # Handle missing keys gracefully
            print(f"Missing key in signal or weights: {e}")
        except Exception as e:
            # Catch-all for unexpected errors
            print(f"Error processing strategy '{strategy}': {e}")

    # Normalize the weighted sum
    if total_confidence > 0:
        final_score = weighted_sum / total_confidence
    else:
        final_score = 0

    # Convert the final score to a signal
    if final_score > 0.2:
        combined_signal = "bullish"
    elif final_score < -0.2:
        combined_signal = "bearish"
    else:
        combined_signal = "neutral"

    return {"signal": combined_signal, "confidence": abs(final_score)}



def normalize_pandas(obj):
    """Convert pandas Series/DataFrames to primitive Python types"""
    if isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict("records")
    elif isinstance(obj, dict):
        return {k: normalize_pandas(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [normalize_pandas(item) for item in obj]
    return obj


##### Main Technical Analyst Function #####
def technical_analyst_agent_yf(data):
    """
    Technical analysis system combining multiple trading strategies for multiple tickers.
    """
    start_date = data["start_date"]
    end_date = data["end_date"]
    tickers = data["tickers"]

    technical_analysis = {}

    for ticker in tickers:
        print(f"Analyzing {ticker}...")

        # Get the historical price data using yfinance
        prices_df = fetch_stock_data(ticker, start_date, end_date)

        if prices_df is None:
            print(f"No price data found for {ticker}. Skipping.")
            continue

        print(f"Calculating trend signals for {ticker}")
        trend_signals = calculate_trend_signals(prices_df)

        print(f"Calculating mean reversion signals for {ticker}")
        mean_reversion_signals = calculate_mean_reversion_signals(prices_df)

        print(f"Calculating momentum signals for {ticker}")
        momentum_signals = calculate_momentum_signals(prices_df)

        print(f"Analyzing volatility for {ticker}")
        volatility_signals = calculate_volatility_signal(prices_df)


        # Combine all signals using a weighted ensemble approach
        strategy_weights = {
            "trend": 0.30,
            "mean_reversion": 0.25,
            "momentum": 0.30,
            "volatility": 0.15,
        }

        print(f"Combining signals for {ticker}")
        combined_signal = weighted_signal_combination(
            {
                "trend": trend_signals,
                "mean_reversion": mean_reversion_signals,
                "momentum": momentum_signals,
                "volatility": volatility_signals,
            },
            strategy_weights,
        )

        # Generate detailed analysis report for this ticker
        technical_analysis[ticker] = {
            "signal": combined_signal["signal"],
            "confidence": round(combined_signal["confidence"] ),
            "strategy_signals": {
                "trend_following": {
                    "signal": trend_signals["signal"],
                    "confidence": round(trend_signals["confidence"] ),
                    "metrics": normalize_pandas(trend_signals["metrics"]),
                },
                "mean_reversion": {
                    "signal": mean_reversion_signals["signal"],
                    "confidence": round(mean_reversion_signals["confidence"] ),
                    "metrics": normalize_pandas(mean_reversion_signals["metrics"]),
                },
                "momentum": {
                    "signal": momentum_signals["signal"],
                    "confidence": round(momentum_signals["confidence"] ),
                    "metrics": normalize_pandas(momentum_signals["metrics"]),
                },
                "volatility": {
                    "signal": volatility_signals["signal"],
                    "confidence": round(volatility_signals["confidence"] ),
                    "metrics": normalize_pandas(volatility_signals["metrics"]),
                },
            },
        }
        print(f"Analysis for {ticker} complete.")

    return json.dumps(technical_analysis)


if __name__ == "__main__":
    data = {
        "start_date": "2024-01-01",
        "end_date": "2025-03-2",
        "tickers": ["TATAPOWER.NS"],  # Add more tickers to test
    }
    result = technical_analyst_agent_yf(data)
    print(result)