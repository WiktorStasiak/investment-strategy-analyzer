"""
====================================================================
Buy & Hold Strategy Analyzer
====================================================================
Autor: Projekt Analizy Danych
Opis:
    Aplikacja do analizy strategii inwestycyjnych "Buy & Hold".
    Użytkownik podaje ticker akcji/ETF z Yahoo Finance, okres czasu,
    częstotliwość dokupywania oraz kwotę inwestycji. Program porównuje
    wyniki strategii z benchmarkiem S&P 500.

Dane:
    Pobierane dynamicznie z Yahoo Finance za pomocą biblioteki yfinance.

Interfejs:
    Stworzony z użyciem biblioteki tkinter z osadzonym wykresem matplotlib.

Struktura projektu:
    main.py              — punkt wejścia
    config.py            — stałe i paleta kolorów
    data/
        fetcher.py       — pobieranie danych z Yahoo Finance
        analyzer.py      — symulacja strategii i metryki inwestycyjne
    ui/
        app.py           — główna klasa okna aplikacji
        left_panel.py    — panel formularza i wyników metryk
        chart_panel.py   — panel wykresu matplotlib
====================================================================
"""

import sys
import os

# Dodaj katalog projektu do ścieżki, aby importy działały niezależnie od CWD
sys.path.insert(0, os.path.dirname(__file__))

from ui.app import InvestmentAnalyzerApp


if __name__ == "__main__":
    app = InvestmentAnalyzerApp()
    app.mainloop()
