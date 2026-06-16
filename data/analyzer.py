"""
Moduł analizy strategii inwestycyjnej Buy & Hold.
Zawiera logikę symulacji portfela oraz obliczania kluczowych metryk inwestycyjnych.
"""

import pandas as pd


def oblicz_strategie_buy_and_hold(
    ceny: pd.DataFrame,
    czestotliwosc: str,
    kwota: float,
) -> pd.DataFrame:
    """
    Symuluje strategię Buy & Hold z regularnym dokupowaniem.

    Zasada działania:
        W każdym wyznaczonym dniu (wg częstotliwości) inwestowana jest stała kwota.
        Kupowane są ułamkowe jednostki akcji po cenie zamknięcia danego dnia.
        Łączna wartość portfela = liczba posiadanych jednostek × bieżąca cena.

    Args:
        ceny:          DataFrame z kolumną 'Close' i indeksem dat.
        czestotliwosc: Kod częstotliwości pandas (np. 'ME', 'W', 'D').
        kwota:         Kwota dokupywana w każdym cyklu (w PLN/USD).

    Returns:
        DataFrame z kolumnami 'wartosc_portfela' i 'zainwestowano', indeksowany datami.
    """
    daty_zakupow = pd.date_range(
        start=ceny.index[0],
        end=ceny.index[-1],
        freq=czestotliwosc,
    )

    # Dopasuj daty zakupów do rzeczywistych dni sesji (najbliższy dzień sesji ≥ daty zakupu)
    daty_sesji = ceny.index
    daty_zakupow_sesja = []
    for data in daty_zakupow:
        dostepne = daty_sesji[daty_sesji >= data]
        if len(dostepne) > 0:
            daty_zakupow_sesja.append(dostepne[0])

    daty_zakupow_sesja = sorted(set(daty_zakupow_sesja))

    jednostki = 0.0     # Całkowita liczba posiadanych jednostek
    zainwestowano = 0.0  # Łączna zainwestowana kwota
    wyniki = []

    for data, row in ceny.iterrows():
        cena = float(row["Close"])

        if data in daty_zakupow_sesja:
            jednostki += kwota / cena
            zainwestowano += kwota

        wyniki.append({
            "data": data,
            "wartosc_portfela": jednostki * cena,
            "zainwestowano": zainwestowano,
        })

    return pd.DataFrame(wyniki).set_index("data")


def oblicz_metryki(wyniki: pd.DataFrame, nazwa: str) -> dict:
    """
    Oblicza kluczowe metryki inwestycyjne dla portfela.

    Args:
        wyniki: DataFrame z kolumnami 'wartosc_portfela' i 'zainwestowano'.
        nazwa:  Nazwa instrumentu (do opisu w wynikach).

    Returns:
        Słownik z kluczami: nazwa, zainwestowano, wartosc_koncowa,
        zysk, zwrot_proc, cagr, max_drawdown.
    """
    zainwestowano = wyniki["zainwestowano"].iloc[-1]
    wartosc_koncowa = wyniki["wartosc_portfela"].iloc[-1]
    zysk = wartosc_koncowa - zainwestowano

    zwrot_proc = (zysk / zainwestowano * 100) if zainwestowano > 0 else 0.0

    # Uproszczony CAGR na bazie końcowej wartości vs zainwestowanego kapitału
    n_lat = (wyniki.index[-1] - wyniki.index[0]).days / 365.25
    if n_lat > 0 and zainwestowano > 0:
        cagr = ((wartosc_koncowa / zainwestowano) ** (1 / n_lat) - 1) * 100
    else:
        cagr = 0.0

    # Maximum Drawdown
    szczyt = wyniki["wartosc_portfela"].cummax()
    obsunięcie = (wyniki["wartosc_portfela"] - szczyt) / szczyt * 100
    max_drawdown = float(obsunięcie.min())

    return {
        "nazwa": nazwa,
        "zainwestowano": zainwestowano,
        "wartosc_koncowa": wartosc_koncowa,
        "zysk": zysk,
        "zwrot_proc": zwrot_proc,
        "cagr": cagr,
        "max_drawdown": max_drawdown,
    }
