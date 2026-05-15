import os
import time
import requests

from dotenv import load_dotenv

load_dotenv()

# Environment Variable
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

if not FINNHUB_API_KEY:
    raise ValueError(
        "FINNHUB_API_KEY environment variable is missing"
    )

BASE_URL = "https://finnhub.io/api/v1"

# Simple in-memory cache
cache = {}

# Cache durations
QUOTE_CACHE_TTL = 15          # seconds
PROFILE_CACHE_TTL = 86400     # 24 hours


class FinnhubError(Exception):
    """Custom exception for Finnhub-related errors"""
    pass


def _get_cached(key):
    """
    Retrieve cached data if valid
    """

    cached = cache.get(key)

    if not cached:
        return None

    if time.time() > cached["expires_at"]:
        del cache[key]
        return None

    return cached["data"]


def _set_cache(key, data, ttl):
    """
    Store data in cache
    """

    cache[key] = {
        "data": data,
        "expires_at": time.time() + ttl,
    }


def _make_request(endpoint, params=None):
    """
    Generic Finnhub request handler
    """

    if params is None:
        params = {}

    url = f"{BASE_URL}{endpoint}"

    headers = {
        "X-Finnhub-Token": FINNHUB_API_KEY
    }

    try:
        response = requests.get(
            url=url,
            params=params,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        return data

    except requests.Timeout:
        raise FinnhubError(
            "Finnhub request timed out"
        )

    except requests.HTTPError:

        if response.status_code == 429:
            raise FinnhubError(
                "Finnhub rate limit exceeded"
            )

        raise FinnhubError(
            f"HTTP Error: {response.status_code}"
        )

    except requests.RequestException as e:
        raise FinnhubError(
            f"Network Error: {str(e)}"
        )

    except Exception as e:
        raise FinnhubError(str(e))


def search_symbol(query: str):
    """
    Search stock symbols using Finnhub

    Example:
    search_symbol("apple")
    """

    cache_key = f"search:{query.lower()}"

    cached = _get_cached(cache_key)

    if cached:
        return cached

    data = _make_request(
        endpoint="/search",
        params={
            "q": query
        }
    )

    results = []

    for item in data.get("result", []):

        symbol = item.get("symbol")

        if not symbol:
            continue

        results.append({
            "symbol": symbol,
            "description": item.get("description"),
            "display_symbol": item.get("displaySymbol"),
            "type": item.get("type"),
        })

    _set_cache(
        cache_key,
        results,
        ttl=300,  # 5 minutes
    )

    return results


def get_company_profile(symbol: str):
    """
    Get company metadata

    Example:
    get_company_profile("AAPL")
    """

    symbol = symbol.upper()

    cache_key = f"profile:{symbol}"

    cached = _get_cached(cache_key)

    if cached:
        return cached

    data = _make_request(
        endpoint="/stock/profile2",
        params={
            "symbol": symbol
        }
    )

    if not data or not data.get("ticker"):
        raise FinnhubError(
            f"No company profile found for {symbol}"
        )

    result = {
        "symbol": data.get("ticker"),
        "company_name": data.get("name"),
        "exchange": data.get("exchange"),
        "industry": data.get("finnhubIndustry"),
        "country": data.get("country"),
        "currency": data.get("currency"),
        "ipo": data.get("ipo"),
        "market_cap": data.get("marketCapitalization"),
        "logo": data.get("logo"),
        "website": data.get("weburl"),
    }

    _set_cache(
        cache_key,
        result,
        ttl=PROFILE_CACHE_TTL,
    )

    return result


def get_stock_quote(symbol: str):
    """
    Get latest stock quote + company data

    Example:
    get_stock_quote("AAPL")
    """

    symbol = symbol.upper()

    cache_key = f"quote:{symbol}"

    cached = _get_cached(cache_key)

    if cached:
        return cached

    # Quote data
    quote_data = _make_request(
        endpoint="/quote",
        params={
            "symbol": symbol
        }
    )

    if not quote_data or quote_data.get("c") == 0:
        raise FinnhubError(
            f"No stock quote found for {symbol}"
        )

    # Company metadata
    profile_data = get_company_profile(symbol)

    result = {
        "symbol": symbol,
        "company_name": profile_data.get("company_name"),
        "exchange": profile_data.get("exchange"),

        # Quote data
        "current_price": quote_data.get("c"),
        "change": quote_data.get("d"),
        "percent_change": quote_data.get("dp"),
        "high": quote_data.get("h"),
        "low": quote_data.get("l"),
        "open": quote_data.get("o"),
        "previous_close": quote_data.get("pc"),

        # Extra metadata
        "industry": profile_data.get("industry"),
        "country": profile_data.get("country"),
        "currency": profile_data.get("currency"),

        # Timestamp
        "timestamp": quote_data.get("t"),
    }

    _set_cache(
        cache_key,
        result,
        ttl=QUOTE_CACHE_TTL,
    )

    return result


if __name__ == "__main__":

    try:

        # Search Example
        print("\nSEARCH RESULTS:")
        results = search_symbol("apple")

        for item in results[:5]:
            print(item)

        # Quote Example
        print("\nSTOCK QUOTE:")
        quote = get_stock_quote("AAPL")

        print(quote)

    except FinnhubError as e:
        print(f"Error: {e}")