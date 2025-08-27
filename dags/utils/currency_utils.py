import time
from datetime import datetime
from airflow.models import Variable  # type:ignore

# Simple cache implementation
_cache = {}
_cache_duration = int(Variable.get("CACHE_DURATION", default_var=86400))


def fetch_exchange_rate():
    """Fetch the latest passed currency to USD exchange rate"""
    try:
        import currencyapicom  # type:ignore
        client = currencyapicom.Client(Variable.get("CURRENCY_API_CLIENT_ID"))
    except ImportError:
        print("Error: currencyapicom module not found. Please install it in your Airflow environment.")
        return None, None
    except Exception as e:
        print(f"Error initializing currency API client: {e}")
        return None, None
    
    current_time = time.time()
    
    # Check if we have cached data and it's still valid
    if ("data" in _cache and 
        "timestamp" in _cache and 
        current_time - _cache["timestamp"] < _cache_duration):
        return _cache["data"], _cache["last_updated"]
    
    try:
        exchanges = client.latest()
        current_datetime = datetime.now()
        
        # Update cache
        _cache["data"] = exchanges["data"]
        _cache["last_updated"] = current_datetime
        _cache["timestamp"] = current_time
        
        return exchanges["data"], current_datetime
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        # Return cached data if available, even if expired
        if "data" in _cache:
            print("Using expired cached data due to API error")
            return _cache["data"], _cache["last_updated"]
        return None, None


def convert_around_usd(amount, currency, direction="to"):
    """convert to usd from currency or to currency from usd

    Args:
        amount (int): amount of money to convert
        currency (string): currency to convert to USD or from USD
        direction (str, optional): values: 'to' and 'from. Defaults to 'to'.

    Returns:
        int: converted value or None if conversion fails
    """
    exchanges, _ = fetch_exchange_rate()
    
    if not exchanges or currency.upper() not in exchanges:
        print(f"Warning: Exchange rate not available for {currency.upper()}")
        return None
    
    try:
        value_to_usd = exchanges[currency.upper()]["value"]
        total = amount / value_to_usd if direction == "to" else amount * value_to_usd
        return round(total, 2)
    except (KeyError, TypeError, ZeroDivisionError) as e:
        print(f"Error converting currency {currency}: {e}")
        return None


def convert_to_usd(amount: int, from_curr: str, round_to: int = 2):
    """Convert amount from specified currency to USD"""
    result = convert_around_usd(amount, from_curr, "to")
    return round(result, round_to) if result is not None else None


def exchange_currencies(amount: int, from_curr: str, to_curr: str, round_to: int = 2):
    """Exchange currencies via USD conversion"""
    from_curr_usd_value = convert_around_usd(amount, from_curr, "to")
    if from_curr_usd_value is None:
        return None
    
    to_curr_usd_equivalent = convert_around_usd(from_curr_usd_value, to_curr, "from")
    return round(to_curr_usd_equivalent, round_to) if to_curr_usd_equivalent is not None else None
