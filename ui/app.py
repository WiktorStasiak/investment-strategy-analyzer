"""
Główna klasa aplikacji Buy & Hold Strategy Analyzer.

Odpowiada za:
- Inicjalizację okna tkinter i zmiennych formularza.
- Koordynację między panelem lewym (formularz) a prawym (wykres).
- Walidację danych wejściowych i uruchomienie analizy w wątku tła.
"""

import threading
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

from config import COLORS, FREQUENCY_OPTIONS, PERIOD_OPTIONS
from data.fetcher import pobierz_dane
from data.analyzer import oblicz_strategie_buy_and_hold, oblicz_metryki
from ui.left_panel import LeftPanel
from ui.chart_panel import ChartPanel


class InvestmentAnalyzerApp(tk.Tk):
    """
    Główne okno aplikacji tkinter łączące panel formularza i panel wykresu.

    Przepływ danych:
        LeftPanel (formularz) → walidacja → wątek tła → pobierz_dane()
        → oblicz_strategie_buy_and_hold() → oblicz_metryki()
        → ChartPanel.wyswietl_wyniki() + LeftPanel.zaktualizuj_metryki()
    """

    def __init__(self):
        super().__init__()

        self.title("Buy & Hold Strategy Analyzer")
        self.configure(bg=COLORS["bg_dark"])
        self.minsize(1080, 720)

        # Zmienne powiązane z polami formularza
        self.var_ticker = tk.StringVar(value="AAPL")
        self.var_benchmark = tk.StringVar(value="^GSPC")
        self.var_kwota = tk.StringVar(value="500")
        self.var_okres = tk.StringVar(value="5 lat")
        self.var_czestotliwosc = tk.StringVar(value="Co miesiąc")
        self.var_status = tk.StringVar(value="Wypełnij formularz i kliknij 'Analizuj'")

        self._zbuduj_ui()

    # ── Budowanie interfejsu ──────────────────────────────────────────────────

    def _zbuduj_ui(self) -> None:
        """Tworzy układ dwukolumnowy: lewy panel formularza + prawy panel wykresu."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._panel_lewy = LeftPanel(
            self,
            var_ticker=self.var_ticker,
            var_benchmark=self.var_benchmark,
            var_kwota=self.var_kwota,
            var_okres=self.var_okres,
            var_czestotliwosc=self.var_czestotliwosc,
            var_status=self.var_status,
            on_analizuj=self._uruchom_analize,
        )
        self._panel_lewy.grid(row=0, column=0, sticky="nsew")

        panel_prawy = tk.Frame(self, bg=COLORS["bg_dark"])
        panel_prawy.grid(row=0, column=1, sticky="nsew")
        panel_prawy.grid_rowconfigure(0, weight=1)
        panel_prawy.grid_columnconfigure(0, weight=1)

        self._panel_wykresu = ChartPanel(panel_prawy, var_status=self.var_status)
        self._panel_wykresu.grid(row=0, column=0, sticky="nsew")

    # ── Logika analizy ────────────────────────────────────────────────────────

    def _uruchom_analize(self) -> None:
        """
        Waliduje dane wejściowe z formularza i uruchamia analizę w wątku tła,
        aby nie blokować pętli zdarzeń tkinter.
        """
        ticker = self.var_ticker.get().strip().upper()
        if not ticker:
            messagebox.showerror("Błąd", "Podaj symbol akcji lub ETF.")
            return

        benchmark = self.var_benchmark.get().strip().upper()

        try:
            kwota = float(self.var_kwota.get().replace(",", "."))
            if kwota <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Błąd", "Kwota inwestycji musi być dodatnią liczbą.")
            return

        n_lat = PERIOD_OPTIONS[self.var_okres.get()]
        czestotliwosc_kod = FREQUENCY_OPTIONS[self.var_czestotliwosc.get()]
        end_date = datetime.today().strftime("%Y-%m-%d")
        start_date = (datetime.today() - timedelta(days=int(n_lat * 365.25))).strftime("%Y-%m-%d")

        self._panel_lewy.ustaw_stan_przycisku("disabled", "⏳  Ładowanie...")
        self.var_status.set(f"Pobieranie danych dla {ticker}...")

        watek = threading.Thread(
            target=self._wykonaj_analize,
            args=(ticker, benchmark, kwota, czestotliwosc_kod, start_date, end_date),
            daemon=True,
        )
        watek.start()

    def _wykonaj_analize(
        self,
        ticker: str,
        benchmark: str,
        kwota: float,
        czestotliwosc_kod: str,
        start_date: str,
        end_date: str,
    ) -> None:
        """
        Właściwa logika analizy (uruchamiana w wątku tła).
        Po zakończeniu przekazuje wyniki do GUI przez self.after().
        """
        try:
            self.after(0, self.var_status.set, f"Pobieranie: {ticker}...")
            ceny_aktywa = pobierz_dane(ticker, start_date, end_date)

            wyniki_benchmark = None
            metryki_benchmark = None

            if benchmark:
                self.after(0, self.var_status.set, f"Pobieranie: {benchmark}...")
                ceny_bench = pobierz_dane(benchmark, start_date, end_date)

                # Wyrównanie do wspólnych dni sesji
                wspolne_daty = ceny_aktywa.index.intersection(ceny_bench.index)
                ceny_aktywa = ceny_aktywa.loc[wspolne_daty]
                ceny_bench = ceny_bench.loc[wspolne_daty]

                wyniki_benchmark = oblicz_strategie_buy_and_hold(
                    ceny_bench, czestotliwosc_kod, kwota)
                metryki_benchmark = oblicz_metryki(wyniki_benchmark, benchmark)

            self.after(0, self.var_status.set, "Obliczanie strategii...")
            wyniki_aktywa = oblicz_strategie_buy_and_hold(
                ceny_aktywa, czestotliwosc_kod, kwota)
            metryki_aktywa = oblicz_metryki(wyniki_aktywa, ticker)

            self.after(0, self._zaktualizuj_gui,
                       wyniki_aktywa, wyniki_benchmark, ceny_aktywa,
                       ticker, benchmark, metryki_aktywa, metryki_benchmark)

        except Exception as e:
            self.after(0, messagebox.showerror, "Błąd analizy", str(e))
            self.after(0, self.var_status.set, f"Błąd: {e}")
        finally:
            self.after(0, self._panel_lewy.ustaw_stan_przycisku,
                       "normal", "▶  ANALIZUJ")

    def _zaktualizuj_gui(
        self,
        wyniki_aktywa,
        wyniki_benchmark,
        ceny_aktywa,
        ticker: str,
        benchmark: str,
        metryki_aktywa: dict,
        metryki_benchmark: dict | None,
    ) -> None:
        """Aktualizuje wykres i metryki w głównym wątku GUI."""
        self._panel_wykresu.wyswietl_wyniki(
            wyniki_aktywa, wyniki_benchmark, ceny_aktywa, ticker, benchmark)
        self._panel_lewy.zaktualizuj_metryki(metryki_aktywa, metryki_benchmark)
        self.var_status.set("✓ Analiza zakończona — dane z Yahoo Finance")
