"""
====================================================================
Investment Strategy Analyzer - Buy & Hold vs S&P 500 Benchmark
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
====================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta


# ─────────────────────────────────────────────
# STAŁE I KONFIGURACJA
# ─────────────────────────────────────────────

SP500_TICKER = "^GSPC"

FREQUENCY_OPTIONS = {
    "Codziennie": "D",
    "Co tydzień": "W",
    "Co miesiąc": "ME",
    "Co kwartał": "QE",
}

PERIOD_OPTIONS = {
    "1 rok": 1,
    "2 lata": 2,
    "3 lata": 3,
    "5 lat": 5,
    "10 lat": 10,
    "20 lat": 20,
}

# Paleta kolorów aplikacji (ciemny motyw finansowy)
COLORS = {
    "bg_dark":      "#0d1117",
    "bg_medium":    "#161b22",
    "bg_light":     "#21262d",
    "border":       "#30363d",
    "accent_blue":  "#58a6ff",
    "accent_green": "#3fb950",
    "accent_red":   "#f85149",
    "accent_gold":  "#e3b341",
    "text_primary": "#f0f6fc",
    "text_secondary":"#8b949e",
    "text_muted":   "#484f58",
    "sp500_color":  "#e3b341",
    "asset_color":  "#58a6ff",
}


# ─────────────────────────────────────────────
# FUNKCJE POBIERANIA I ANALIZY DANYCH
# ─────────────────────────────────────────────

def pobierz_dane(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Pobiera historyczne dane cenowe z Yahoo Finance.

    Args:
        ticker: Symbol giełdowy (np. 'AAPL', 'SPY', '^GSPC')
        start_date: Data początkowa w formacie 'YYYY-MM-DD'
        end_date: Data końcowa w formacie 'YYYY-MM-DD'

    Returns:
        DataFrame z kolumną 'Close' i indeksem dat.

    Raises:
        ValueError: Gdy nie uda się pobrać danych lub ticker jest nieprawidłowy.
    """
    dane = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)

    if dane.empty:
        raise ValueError(f"Nie znaleziono danych dla tickera: '{ticker}'.\n"
                         "Sprawdź poprawność symbolu na finance.yahoo.com")

    # Spłaszcz kolumny MultiIndex jeśli istnieje
    if isinstance(dane.columns, pd.MultiIndex):
        dane.columns = dane.columns.get_level_values(0)

    return dane[["Close"]].dropna()


def oblicz_strategie_buy_and_hold(ceny: pd.DataFrame,
                                   czestotliwosc: str,
                                   kwota: float) -> pd.DataFrame:
    """
    Symuluje strategię Buy & Hold z regularnym dokupowaniem.

    Zasada działania:
    - W każdym wyznaczonym dniu (wg częstotliwości) inwestowana jest stała kwota.
    - Kupowane są ułamkowe jednostki akcji po cenie zamknięcia danego dnia.
    - Łączna wartość portfela = liczba posiadanych jednostek × bieżąca cena.

    Args:
        ceny: DataFrame z kolumną 'Close' i indeksem dat.
        czestotliwosc: Kod częstotliwości pandas (np. 'ME', 'W', 'D').
        kwota: Kwota dokupywana w każdym cyklu (w PLN/USD).

    Returns:
        DataFrame z kolumnami: 'wartosc_portfela', 'zainwestowano'.
    """
    # Generuj daty zakupów wg wybranej częstotliwości
    daty_zakupow = pd.date_range(
        start=ceny.index[0],
        end=ceny.index[-1],
        freq=czestotliwosc
    )

    # Dopasuj daty zakupów do rzeczywistych dni sesji (najbliższy dzień sesji)
    daty_sesji = ceny.index
    daty_zakupow_sesja = []
    for data in daty_zakupow:
        # Znajdź najbliższą datę sesji >= data zakupu
        dostepne = daty_sesji[daty_sesji >= data]
        if len(dostepne) > 0:
            daty_zakupow_sesja.append(dostepne[0])

    daty_zakupow_sesja = sorted(set(daty_zakupow_sesja))

    # Symulacja portfela
    jednostki = 0.0        # Całkowita liczba posiadanych jednostek
    zainwestowano = 0.0    # Łączna zainwestowana kwota

    wyniki = []

    for data, row in ceny.iterrows():
        cena = float(row["Close"])

        # Jeśli to dzień zakupu, dokup jednostki
        if data in daty_zakupow_sesja:
            jednostki += kwota / cena
            zainwestowano += kwota

        wartosc = jednostki * cena
        wyniki.append({
            "data": data,
            "wartosc_portfela": wartosc,
            "zainwestowano": zainwestowano
        })

    df = pd.DataFrame(wyniki).set_index("data")
    return df


def oblicz_metryki(wyniki: pd.DataFrame, nazwa: str) -> dict:
    """
    Oblicza kluczowe metryki inwestycyjne dla portfela.

    Args:
        wyniki: DataFrame z wynikami strategii.
        nazwa: Nazwa instrumentu (do opisu).

    Returns:
        Słownik z metrykami: zysk, zwrot_proc, max_drawdown, cagr.
    """
    zainwestowano = wyniki["zainwestowano"].iloc[-1]
    wartosc_koncowa = wyniki["wartosc_portfela"].iloc[-1]
    zysk = wartosc_koncowa - zainwestowano

    # Zwrot procentowy
    zwrot_proc = (zysk / zainwestowano * 100) if zainwestowano > 0 else 0

    # CAGR (Compound Annual Growth Rate)
    n_lat = (wyniki.index[-1] - wyniki.index[0]).days / 365.25
    if n_lat > 0 and zainwestowano > 0:
        # Uproszczony CAGR na bazie końcowej wartości vs zainwestowanego kapitału
        cagr = ((wartosc_koncowa / zainwestowano) ** (1 / n_lat) - 1) * 100
    else:
        cagr = 0

    # Maximum Drawdown
    szczyt = wyniki["wartosc_portfela"].cummax()
    obsunięcie = (wyniki["wartosc_portfela"] - szczyt) / szczyt * 100
    max_drawdown = obsunięcie.min()

    return {
        "nazwa": nazwa,
        "zainwestowano": zainwestowano,
        "wartosc_koncowa": wartosc_koncowa,
        "zysk": zysk,
        "zwrot_proc": zwrot_proc,
        "cagr": cagr,
        "max_drawdown": max_drawdown,
    }


# ─────────────────────────────────────────────
# KLASA GŁÓWNA APLIKACJI
# ─────────────────────────────────────────────

class InvestmentAnalyzerApp(tk.Tk):
    """
    Główna klasa aplikacji tkinter.

    Odpowiada za:
    - Budowanie interfejsu graficznego
    - Obsługę zdarzeń użytkownika
    - Koordynację pobierania danych i wyświetlania wykresów
    """

    def __init__(self):
        super().__init__()

        self.title("Investment Analyzer — Buy & Hold Strategy")
        self.configure(bg=COLORS["bg_dark"])
        self.minsize(1080, 720)

        # Zmienne tkinter powiązane z polami formularza
        self.var_ticker = tk.StringVar(value="AAPL")
        self.var_benchmark = tk.StringVar(value="^GSPC")
        self.var_kwota = tk.StringVar(value="500")
        self.var_okres = tk.StringVar(value="5 lat")
        self.var_czestotliwosc = tk.StringVar(value="Co miesiąc")
        self.var_status = tk.StringVar(value="Wypełnij formularz i kliknij 'Analizuj'")

        self._zbuduj_ui()

    # ── Budowanie interfejsu ──────────────────

    def _zbuduj_ui(self):
        """Konstruuje cały interfejs graficzny aplikacji."""

        # Główny kontener z dwoma kolumnami: panel lewy (formularz) + prawy (wykres)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Panel lewy (kontrolki) ──
        panel_lewy = tk.Frame(self, bg=COLORS["bg_medium"],
                              width=350, relief="flat")  # Zwiększona szerokość
        panel_lewy.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        panel_lewy.grid_propagate(False)

        self._zbuduj_panel_lewy(panel_lewy)

        # ── Panel prawy (wykres) ──
        panel_prawy = tk.Frame(self, bg=COLORS["bg_dark"])
        panel_prawy.grid(row=0, column=1, sticky="nsew")
        panel_prawy.grid_rowconfigure(0, weight=1)
        panel_prawy.grid_columnconfigure(0, weight=1)

        self._zbuduj_panel_wykresu(panel_prawy)

    def _zbuduj_panel_lewy(self, rodzic):
        """Buduje lewy panel z formularzem wejściowym."""

        # ── Nagłówek ──
        naglowek = tk.Frame(rodzic, bg=COLORS["bg_dark"], pady=6)
        naglowek.pack(fill="x")

        tk.Label(naglowek, text="📈", font=("Segoe UI Emoji", 18),
                 bg=COLORS["bg_dark"], fg=COLORS["accent_blue"]).pack()
        tk.Label(naglowek, text="Investment Analyzer",
                 font=("Georgia", 12, "bold"),
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                 justify="center").pack()

        # ── Separator ──
        tk.Frame(rodzic, bg=COLORS["border"], height=1).pack(fill="x")

        # ── Formularz ──
        formularz = tk.Frame(rodzic, bg=COLORS["bg_medium"], padx=20, pady=4)
        formularz.pack(fill="both", expand=True)

        self._pole_formularza(formularz, "Ticker instrumentu z Yahoo! Finance",
                              "np. AAPL, MSFT, SPY, QQQ", self.var_ticker)

        self._pole_formularza(formularz, "Ticker benchmark z Yahoo! Finance",
                              "np. ^GSPC, QQQ, GLD, BTC-USD", self.var_benchmark)

        self._pole_formularza(formularz, "Kwota inwestycji",
                              "np. 500", self.var_kwota, typ="number")

        self._lista_rozwijalna(formularz, "Okres analizy", self.var_okres,
                               list(PERIOD_OPTIONS.keys()))

        self._lista_rozwijalna(formularz, "Częstotliwość dokupowania",
                               self.var_czestotliwosc,
                               list(FREQUENCY_OPTIONS.keys()))

        # ── Przycisk analizy ──
        tk.Frame(formularz, height=5, bg=COLORS["bg_medium"]).pack()

        self.btn_analizuj = tk.Button(
            formularz,
            text="▶  ANALIZUJ",
            command=self._uruchom_analize,
            bg=COLORS["accent_blue"],
            fg=COLORS["bg_dark"],
            font=("Courier", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=10, pady=10,
            activebackground="#79c0ff",
            activeforeground=COLORS["bg_dark"],
        )
        self.btn_analizuj.pack(fill="x", ipady=4)

        # Hover efekt na przycisku
        self.btn_analizuj.bind("<Enter>", lambda e: self.btn_analizuj.config(bg="#79c0ff"))
        self.btn_analizuj.bind("<Leave>", lambda e: self.btn_analizuj.config(bg=COLORS["accent_blue"]))

        # ── Pasek statusu ──
        tk.Frame(formularz, height=6, bg=COLORS["bg_medium"]).pack()
        tk.Frame(rodzic, bg=COLORS["border"], height=1).pack(fill="x")

        status_frame = tk.Frame(rodzic, bg=COLORS["bg_dark"], pady=4, padx=16)
        status_frame.pack(fill="x")
        tk.Label(status_frame, textvariable=self.var_status,
                 bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                 font=("Courier", 8), wraplength=240, justify="left").pack(anchor="w")

        # ── Panel metryk (wypełniany po analizie) — dwie kolumny ──
        tk.Frame(rodzic, bg=COLORS["border"], height=1).pack(fill="x")
        self.panel_metryk = tk.Frame(rodzic, bg=COLORS["bg_medium"], padx=0, pady=0)
        self.panel_metryk.pack(fill="both", expand=True)

        tk.Label(self.panel_metryk, text="Wyniki analizy",
                 bg=COLORS["bg_medium"], fg=COLORS["text_muted"],
                 font=("Courier", 9, "bold"),
                 padx=16).pack(anchor="w", pady=(5, 2))

        # Kontener ułożony w siatce na dwie kolumny wyników
        self.metryki_kolumny = tk.Frame(self.panel_metryk, bg=COLORS["bg_medium"])
        self.metryki_kolumny.pack(fill="both", expand=True, padx=10)
        self.metryki_kolumny.grid_columnconfigure(0, weight=1)
        self.metryki_kolumny.grid_columnconfigure(1, weight=1)

        # Lewa kolumna - Główny instrument
        self.lbl_metryki_aktywo = tk.Text(
            self.metryki_kolumny,
            bg=COLORS["bg_medium"],
            fg=COLORS["text_secondary"],
            font=("Courier", 9),
            relief="flat",
            bd=0,
            padx=5,
            pady=4,
            wrap="word",
            state="disabled",
            cursor="arrow",
            width=15
        )
        self.lbl_metryki_aktywo.grid(row=0, column=0, sticky="nsew")

        # Prawa kolumna - Benchmark
        self.lbl_metryki_benchmark = tk.Text(
            self.metryki_kolumny,
            bg=COLORS["bg_medium"],
            fg=COLORS["text_secondary"],
            font=("Courier", 9),
            relief="flat",
            bd=0,
            padx=5,
            pady=4,
            wrap="word",
            state="disabled",
            cursor="arrow",
            width=15
        )
        self.lbl_metryki_benchmark.grid(row=0, column=1, sticky="nsew")

    def _pole_formularza(self, rodzic, etykieta, placeholder, zmienna, typ="text"):
        """Tworzy pole tekstowe z etykietą."""
        ramka = tk.Frame(rodzic, bg=COLORS["bg_medium"])
        ramka.pack(fill="x", pady=(5, 0))

        tk.Label(ramka, text=etykieta,
                 bg=COLORS["bg_medium"], fg=COLORS["text_secondary"],
                 font=("Courier", 8, "bold")).pack(anchor="w")

        entry = tk.Entry(
            ramka,
            textvariable=zmienna,
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["accent_blue"],
            relief="flat",
            font=("Courier", 11),
            bd=6,
        )
        entry.pack(fill="x", ipady=2)

        tk.Label(ramka, text=placeholder,
                 bg=COLORS["bg_medium"], fg=COLORS["text_muted"],
                 font=("Courier", 7)).pack(anchor="w")

    def _lista_rozwijalna(self, rodzic, etykieta, zmienna, opcje):
        """Tworzy listę rozwijalną (Combobox) z etykietą."""
        ramka = tk.Frame(rodzic, bg=COLORS["bg_medium"])
        ramka.pack(fill="x", pady=(5, 0))

        tk.Label(ramka, text=etykieta,
                 bg=COLORS["bg_medium"], fg=COLORS["text_secondary"],
                 font=("Courier", 8, "bold")).pack(anchor="w")

        # Stylizacja Combobox
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TCombobox",
                        fieldbackground=COLORS["bg_light"],
                        background=COLORS["bg_light"],
                        foreground=COLORS["text_primary"],
                        selectbackground=COLORS["accent_blue"],
                        selectforeground=COLORS["bg_dark"],
                        bordercolor=COLORS["border"],
                        arrowcolor=COLORS["accent_blue"])

        combo = ttk.Combobox(ramka, textvariable=zmienna,
                             values=opcje, state="readonly",
                             style="Dark.TCombobox",
                             font=("Courier", 10))
        combo.pack(fill="x", ipady=4)

    def _zbuduj_panel_wykresu(self, rodzic):
        """Buduje panel z wykresem matplotlib."""

        # Figura matplotlib z ciemnym tłem
        self.fig = Figure(figsize=(10,7), facecolor=COLORS["bg_dark"])
        self.fig.subplots_adjust(left=0.13, right=0.95, top=0.88, bottom=0.25,
                                  hspace=0.4)

        # Dwa subploty: górny (wartość portfela) + dolny (zwrot %)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)

        for ax in (self.ax1, self.ax2):
            ax.set_facecolor(COLORS["bg_medium"])
            for spine in ax.spines.values():
                spine.set_color(COLORS["border"])
            ax.tick_params(colors=COLORS["text_secondary"], labelsize=8)
            ax.xaxis.label.set_color(COLORS["text_secondary"])
            ax.yaxis.label.set_color(COLORS["text_secondary"])

        self.ax1.set_title("Wartość portfela w czasie",
                           color=COLORS["text_primary"], fontsize=11, pad=10,
                           fontfamily="monospace")
        self.ax2.set_title("Skumulowany zwrot (%)",
                           color=COLORS["text_primary"], fontsize=11, pad=10,
                           fontfamily="monospace")

        # Osadź wykres w oknie tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=rodzic)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Pasek z pojedynczym przyciskiem zapisu wykresu
        toolbar_frame = tk.Frame(rodzic, bg=COLORS["bg_dark"], pady=4)
        toolbar_frame.grid(row=1, column=0, sticky="ew")

        btn_zapisz = tk.Button(
            toolbar_frame,
            text="\U0001f4be  Zapisz wykres",
            command=self._zapisz_wykres,
            bg=COLORS["bg_light"],
            fg=COLORS["text_secondary"],
            font=("Courier", 9),
            relief="flat",
            cursor="hand2",
            padx=12, pady=4,
            activebackground=COLORS["border"],
            activeforeground=COLORS["text_primary"],
        )
        btn_zapisz.pack(side="right", padx=10)
        btn_zapisz.bind("<Enter>", lambda e: btn_zapisz.config(
            bg=COLORS["border"], fg=COLORS["text_primary"]))
        btn_zapisz.bind("<Leave>", lambda e: btn_zapisz.config(
            bg=COLORS["bg_light"], fg=COLORS["text_secondary"]))

        self._wyswietl_ekran_startowy()

    def _zapisz_wykres(self):
        """Otwiera dialog zapisu i zapisuje bieżący wykres do pliku PNG/PDF/SVG."""
        from tkinter import filedialog
        sciezka = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("PDF", "*.pdf"),
                ("SVG", "*.svg"),
            ],
            title="Zapisz wykres",
            initialfile="wykres_inwestycji",
        )
        if sciezka:
            self.fig.savefig(sciezka, dpi=150, bbox_inches="tight",
                             facecolor=self.fig.get_facecolor())
            self.var_status.set(f"✓ Wykres zapisany: {sciezka}")

    def _wyswietl_ekran_startowy(self):
        """Wyświetla ekran powitalny na wykresie przed uruchomieniem analizy."""
        for ax in (self.ax1, self.ax2):
            ax.clear()
            ax.set_facecolor(COLORS["bg_medium"])
            for spine in ax.spines.values():
                spine.set_color(COLORS["border"])

        self.ax1.text(0.5, 0.5,
                      "Wprowadź parametry i kliknij 'Analizuj'\naby zobaczyć wyniki",
                      transform=self.ax1.transAxes,
                      ha="center", va="center",
                      color=COLORS["text_muted"], fontsize=13,
                      fontfamily="monospace")
        self.ax2.text(0.5, 0.5,
                      "Benchmark: S&P 500  |  Strategia: Buy & Hold",
                      transform=self.ax2.transAxes,
                      ha="center", va="center",
                      color=COLORS["text_muted"], fontsize=10,
                      fontfamily="monospace")

        self.canvas.draw()

    # ── Logika analizy ────────────────────────

    def _uruchom_analize(self):
        """
        Waliduje dane wejściowe i uruchamia analizę w osobnym wątku,
        aby nie blokować interfejsu.
        """
        # Walidacja tickera
        ticker = self.var_ticker.get().strip().upper()
        if not ticker:
            messagebox.showerror("Błąd", "Podaj symbol akcji lub ETF.")
            return

        # Benchmark jest opcjonalny — pusty string = brak porównania
        benchmark = self.var_benchmark.get().strip().upper()

        # Walidacja kwoty
        try:
            kwota = float(self.var_kwota.get().replace(",", "."))
            if kwota <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Błąd", "Kwota inwestycji musi być dodatnią liczbą.")
            return

        # Pobranie parametrów
        n_lat = PERIOD_OPTIONS[self.var_okres.get()]
        czestotliwosc_kod = FREQUENCY_OPTIONS[self.var_czestotliwosc.get()]

        end_date = datetime.today().strftime("%Y-%m-%d")
        start_date = (datetime.today() - timedelta(days=int(n_lat * 365.25))).strftime("%Y-%m-%d")

        # Blokada przycisku podczas analizy
        self.btn_analizuj.config(state="disabled", text="⏳  Ładowanie...")
        self.var_status.set(f"Pobieranie danych dla {ticker}...")

        # Uruchomienie w wątku tła
        watek = threading.Thread(
            target=self._wykonaj_analize,
            args=(ticker, benchmark, kwota, czestotliwosc_kod, start_date, end_date),
            daemon=True,
        )
        watek.start()

    def _wykonaj_analize(self, ticker, benchmark, kwota, czestotliwosc_kod,
                          start_date, end_date):
        """
        Właściwa logika analizy (uruchamiana w wątku tła).
        Po zakończeniu aktualizuje GUI w głównym wątku.
        """
        try:
            self.after(0, self.var_status.set, f"Pobieranie: {ticker}...")
            ceny_aktywa = pobierz_dane(ticker, start_date, end_date)

            wyniki_benchmark = None
            metryki_benchmark = None

            if benchmark:
                self.after(0, self.var_status.set, f"Pobieranie: {benchmark}...")
                ceny_bench = pobierz_dane(benchmark, start_date, end_date)

                # Wyrównaj daty do wspólnych dni sesji
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

            # Aktualizuj GUI w głównym wątku
            self.after(0, self._zaktualizuj_wykres,
                       wyniki_aktywa, wyniki_benchmark, ceny_aktywa, ticker, benchmark,
                       metryki_aktywa, metryki_benchmark, kwota)

        except Exception as e:
            self.after(0, messagebox.showerror, "Błąd analizy", str(e))
            self.after(0, self.var_status.set, f"Błąd: {e}")
        finally:
            self.after(0, self.btn_analizuj.config,
                       {"state": "normal", "text": "▶  ANALIZUJ"})

    def _zaktualizuj_wykres(self, wyniki_aktywa, wyniki_benchmark, ceny_aktywa,
                             ticker, benchmark,
                             metryki_aktywa, metryki_benchmark, kwota):
        """
        Rysuje wykresy na podstawie obliczonych danych.

        Wykres dolny:
        - Brak benchmarku → wykres cen historycznych (surowe ceny zamknięcia)
        - Z benchmarkiem  → skumulowany zwrot z inwestycji (%)

        Poprawka zakresu osi X: ax.set_xlim() ustawia dokładny zakres danych,
        dzięki czemu zmiana okresu analizy zawsze odświeża oś czasu.
        """
        for ax in (self.ax1, self.ax2):
            ax.clear()
            ax.set_facecolor(COLORS["bg_medium"])
            for spine in ax.spines.values():
                spine.set_color(COLORS["border"])
            ax.tick_params(colors=COLORS["text_secondary"], labelsize=8)
            ax.grid(True, color=COLORS["border"], linewidth=0.5, alpha=0.7)

        # Dokładny zakres dat z aktualnych danych — zapobiega "pamięci" poprzednich zakresów
        x_min = wyniki_aktywa.index[0]
        x_max = wyniki_aktywa.index[-1]

        tytul1 = f"Wartość portfela – {ticker}"
        if benchmark:
            tytul1 += f" vs {benchmark}"

        # ── Wykres 1: Wartość portfela ──
        if wyniki_benchmark is not None:
            self.ax1.plot(wyniki_benchmark.index, wyniki_benchmark["wartosc_portfela"],
                          color=COLORS["sp500_color"], linewidth=2,
                          label=benchmark, zorder=3)
        self.ax1.plot(wyniki_aktywa.index, wyniki_aktywa["wartosc_portfela"],
                      color=COLORS["asset_color"], linewidth=2,
                      label=ticker, zorder=4)
        self.ax1.plot(wyniki_aktywa.index, wyniki_aktywa["zainwestowano"],
                      color=COLORS["text_muted"], linewidth=1.2,
                      linestyle="--", label="Zainwestowany kapitał", zorder=2)

        self.ax1.set_xlim(x_min, x_max)
        self.ax1.set_title(tytul1, color=COLORS["text_primary"], fontsize=11,
                           pad=10, fontfamily="monospace")
        self.ax1.set_ylabel("Wartość (USD)", color=COLORS["text_secondary"],
                            fontsize=8, fontfamily="monospace")
        self.ax1.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        self.ax1.legend(facecolor=COLORS["bg_dark"], edgecolor=COLORS["border"],
                        labelcolor=COLORS["text_primary"], fontsize=8)

        # ── Wykres 2: ceny historyczne LUB skumulowany zwrot ──
        if wyniki_benchmark is None:
            # Tryb bez benchmarku: wykres surowych cen zamknięcia
            ceny = ceny_aktywa["Close"].values
            self.ax2.plot(ceny_aktywa.index, ceny,
                          color=COLORS["asset_color"], linewidth=1.5,
                          label=f"{ticker} – cena zamknięcia", zorder=4)

            # Gradient wypełnienia pod linią ceny
            self.ax2.fill_between(ceny_aktywa.index, ceny, ceny.min(),
                                   alpha=0.12, color=COLORS["asset_color"])

            self.ax2.set_xlim(x_min, x_max)
            self.ax2.set_title(f"Ceny historyczne – {ticker}",
                               color=COLORS["text_primary"], fontsize=11,
                               pad=10, fontfamily="monospace")
            self.ax2.set_ylabel("Cena (USD)", color=COLORS["text_secondary"],
                                fontsize=8, fontfamily="monospace")
            self.ax2.yaxis.set_major_formatter(
                mticker.FuncFormatter(lambda x, _: f"${x:,.2f}"))

        else:
            # Tryb z benchmarkiem: skumulowany zwrot z inwestycji
            zwrot_aktywa = ((wyniki_aktywa["wartosc_portfela"] /
                             wyniki_aktywa["zainwestowano"]) - 1) * 100
            zwrot_benchmark = ((wyniki_benchmark["wartosc_portfela"] /
                                wyniki_benchmark["zainwestowano"]) - 1) * 100

            self.ax2.axhline(0, color=COLORS["border"], linewidth=1, zorder=1)
            self.ax2.plot(wyniki_benchmark.index, zwrot_benchmark,
                          color=COLORS["sp500_color"], linewidth=2,
                          label=benchmark, zorder=3)
            self.ax2.plot(wyniki_aktywa.index, zwrot_aktywa,
                          color=COLORS["asset_color"], linewidth=2,
                          label=ticker, zorder=4)

            self.ax2.fill_between(wyniki_aktywa.index, zwrot_aktywa, 0,
                                   where=(zwrot_aktywa >= 0),
                                   alpha=0.15, color=COLORS["accent_green"])
            self.ax2.fill_between(wyniki_aktywa.index, zwrot_aktywa, 0,
                                   where=(zwrot_aktywa < 0),
                                   alpha=0.15, color=COLORS["accent_red"])

            self.ax2.set_xlim(x_min, x_max)
            self.ax2.set_title("Skumulowany zwrot z inwestycji (%)",
                               color=COLORS["text_primary"], fontsize=11,
                               pad=10, fontfamily="monospace")
            self.ax2.set_ylabel("Zwrot (%)", color=COLORS["text_secondary"],
                                fontsize=8, fontfamily="monospace")
            self.ax2.yaxis.set_major_formatter(
                mticker.FuncFormatter(lambda x, _: f"{x:+.1f}%"))

        self.ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        self.ax2.legend(facecolor=COLORS["bg_dark"], edgecolor=COLORS["border"],
                        labelcolor=COLORS["text_primary"], fontsize=8)

        # Etykiety osi X
        for ax in (self.ax1, self.ax2):
            ax.tick_params(axis="x", colors=COLORS["text_secondary"])

        self.canvas.draw()

        # ── Aktualizacja metryk ──
        self._zaktualizuj_metryki(metryki_aktywa, metryki_benchmark)
        self.var_status.set(
            f"✓ Analiza zakończona — dane z Yahoo Finance"
        )

    def _zaktualizuj_metryki(self, metryki_aktywa, metryki_benchmark):
        """Aktualizuje panel z kluczowymi metrykami inwestycyjnymi."""

        def fmt_usd(v):
            return f"${v:,.2f}"

        def fmt_proc(v):
            znak = "+" if v >= 0 else ""
            return f"{znak}{v:.1f}%"

        def blok(m, suffix=""):
            nazwa = m['nazwa'] + (f"\n({suffix})" if suffix else "")
            return (
                f"{nazwa}\n"
                f"Zainwest: {fmt_usd(m['zainwestowano'])}\n"
                f"Wart.koń: {fmt_usd(m['wartosc_koncowa'])}\n"
                f"Zysk/Str: {fmt_usd(m['zysk'])}\n"
                f"Zwrot:    {fmt_proc(m['zwrot_proc'])}\n"
                f"CAGR:     {fmt_proc(m['cagr'])}\n"
                f"Max DD:   {m['max_drawdown']:.1f}%"
            )

        # Aktualizacja kolumny lewej (instrument)
        self.lbl_metryki_aktywo.config(state="normal")
        self.lbl_metryki_aktywo.delete("1.0", "end")
        self.lbl_metryki_aktywo.insert("1.0", blok(metryki_aktywa))
        self.lbl_metryki_aktywo.config(state="disabled")

        # Aktualizacja kolumny prawej (benchmark)
        self.lbl_metryki_benchmark.config(state="normal")
        self.lbl_metryki_benchmark.delete("1.0", "end")
        if metryki_benchmark is not None:
            self.lbl_metryki_benchmark.insert("1.0", blok(metryki_benchmark, "benchmark"))
        self.lbl_metryki_benchmark.config(state="disabled")


# ─────────────────────────────────────────────
# PUNKT WEJŚCIA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = InvestmentAnalyzerApp()
    app.mainloop()