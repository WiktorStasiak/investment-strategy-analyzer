"""
Moduł pobierania danych historycznych z Yahoo Finance za pomocą biblioteki yfinance.
"""

import pandas as pd
import yfinance as yf


def pobierz_dane(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Pobiera historyczne dane cenowe z Yahoo Finance.

    Args:
        ticker:     Symbol giełdowy (np. 'AAPL', 'SPY', '^GSPC').
        start_date: Data początkowa w formacie 'YYYY-MM-DD'.
        end_date:   Data końcowa w formacie 'YYYY-MM-DD'.

    Returns:
        DataFrame z kolumną 'Close' i indeksem dat (bez wartości NaN).

    Raises:
        ValueError: Gdy ticker jest nieprawidłowy lub brak danych dla podanego okresu.
    """
    dane = yf.download(ticker, start=start_date, end=end_date,
                       progress=False, auto_adjust=True)

    if dane.empty:
        raise ValueError(
            f"Nie znaleziono danych dla tickera: '{ticker}'.\n"
            "Sprawdź poprawność symbolu na finance.yahoo.com"
        )

    # Spłaszcz kolumny MultiIndex, jeśli istnieje (zdarza się przy niektórych tickerach)
    if isinstance(dane.columns, pd.MultiIndex):
        dane.columns = dane.columns.get_level_values(0)

    return dane[["Close"]].dropna()
