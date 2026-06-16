"""
Lewy panel interfejsu graficznego aplikacji Investment Analyzer.

Zawiera:
- Formularz wejściowy (ticker, benchmark, kwota, okres, częstotliwość).
- Przycisk uruchamiający analizę.
- Pasek statusu.
- Panel z wynikami metryk inwestycyjnych po zakończeniu analizy.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable

from config import COLORS, FREQUENCY_OPTIONS, PERIOD_OPTIONS


class LeftPanel(tk.Frame):
    """
    Panel formularza i wyników (lewa kolumna okna głównego).

    Args:
        rodzic:            Widget nadrzędny tkinter.
        var_ticker:        StringVar z symbolem głównego instrumentu.
        var_benchmark:     StringVar z symbolem benchmarku (opcjonalny).
        var_kwota:         StringVar z kwotą inwestycji.
        var_okres:         StringVar z wybranym okresem analizy.
        var_czestotliwosc: StringVar z wybraną częstotliwością.
        var_status:        StringVar z komunikatem statusu.
        on_analizuj:       Callback wywoływany po kliknięciu przycisku "Analizuj".
    """

    def __init__(
        self,
        rodzic: tk.Widget,
        var_ticker: tk.StringVar,
        var_benchmark: tk.StringVar,
        var_kwota: tk.StringVar,
        var_okres: tk.StringVar,
        var_czestotliwosc: tk.StringVar,
        var_status: tk.StringVar,
        on_analizuj: Callable,
        **kwargs,
    ):
        super().__init__(rodzic, bg=COLORS["bg_medium"], width=350,
                         relief="flat", **kwargs)
        self.grid_propagate(False)

        self._var_ticker = var_ticker
        self._var_benchmark = var_benchmark
        self._var_kwota = var_kwota
        self._var_okres = var_okres
        self._var_czestotliwosc = var_czestotliwosc
        self._var_status = var_status
        self._on_analizuj = on_analizuj

        self._zbuduj()

    # ── Budowanie panelu ──────────────────────────────────────────────────────

    def _zbuduj(self) -> None:
        """Buduje wszystkie sekcje lewego panelu."""
        self._zbuduj_naglowek()
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x")
        self._zbuduj_formularz()
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x")
        self._zbuduj_pasek_statusu()
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x")
        self._zbuduj_panel_metryk()

    def _zbuduj_naglowek(self) -> None:
        """Nagłówek z ikoną i tytułem aplikacji."""
        naglowek = tk.Frame(self, bg=COLORS["bg_dark"], pady=6)
        naglowek.pack(fill="x")

        tk.Label(naglowek, text="📈", font=("Segoe UI Emoji", 18),
                 bg=COLORS["bg_dark"], fg=COLORS["accent_blue"]).pack()
        tk.Label(naglowek, text="Investment Analyzer",
                 font=("Georgia", 12, "bold"),
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                 justify="center").pack()

    def _zbuduj_formularz(self) -> None:
        """Formularz z polami wejściowymi i przyciskiem analizy."""
        formularz = tk.Frame(self, bg=COLORS["bg_medium"], padx=20, pady=4)
        formularz.pack(fill="both", expand=True)

        self._pole_formularza(formularz, "Ticker instrumentu z Yahoo! Finance",
                              "np. AAPL, MSFT, SPY, QQQ", self._var_ticker)

        self._pole_formularza(formularz, "Ticker benchmark z Yahoo! Finance",
                              "np. ^GSPC, QQQ, GLD, BTC-USD", self._var_benchmark)

        self._pole_formularza(formularz, "Kwota inwestycji",
                              "np. 500", self._var_kwota, typ="number")

        self._lista_rozwijalna(formularz, "Okres analizy",
                               self._var_okres, list(PERIOD_OPTIONS.keys()))

        self._lista_rozwijalna(formularz, "Częstotliwość dokupowania",
                               self._var_czestotliwosc, list(FREQUENCY_OPTIONS.keys()))

        tk.Frame(formularz, height=5, bg=COLORS["bg_medium"]).pack()
        self._zbuduj_przycisk_analizy(formularz)

    def _zbuduj_przycisk_analizy(self, rodzic: tk.Widget) -> None:
        """Przycisk uruchamiający analizę z efektem hover."""
        self.btn_analizuj = tk.Button(
            rodzic,
            text="▶  ANALIZUJ",
            command=self._on_analizuj,
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
        self.btn_analizuj.bind("<Enter>",
                               lambda e: self.btn_analizuj.config(bg="#79c0ff"))
        self.btn_analizuj.bind("<Leave>",
                               lambda e: self.btn_analizuj.config(bg=COLORS["accent_blue"]))

    def _zbuduj_pasek_statusu(self) -> None:
        """Pasek statusu z bieżącym komunikatem operacji."""
        tk.Frame(self, height=6, bg=COLORS["bg_medium"]).pack()
        status_frame = tk.Frame(self, bg=COLORS["bg_dark"], pady=4, padx=16)
        status_frame.pack(fill="x")
        tk.Label(status_frame, textvariable=self._var_status,
                 bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                 font=("Courier", 8), wraplength=240, justify="left").pack(anchor="w")

    def _zbuduj_panel_metryk(self) -> None:
        """Panel z wynikami metryk w układzie dwukolumnowym."""
        panel = tk.Frame(self, bg=COLORS["bg_medium"], padx=0, pady=0)
        panel.pack(fill="both", expand=True)

        tk.Label(panel, text="Wyniki analizy",
                 bg=COLORS["bg_medium"], fg=COLORS["text_muted"],
                 font=("Courier", 9, "bold"),
                 padx=16).pack(anchor="w", pady=(5, 2))

        kolumny = tk.Frame(panel, bg=COLORS["bg_medium"])
        kolumny.pack(fill="both", expand=True, padx=10)
        kolumny.grid_columnconfigure(0, weight=1)
        kolumny.grid_columnconfigure(1, weight=1)

        wspolne = dict(
            bg=COLORS["bg_medium"],
            fg=COLORS["text_secondary"],
            font=("Courier", 9),
            relief="flat", bd=0,
            padx=5, pady=4,
            wrap="word",
            state="disabled",
            cursor="arrow",
            width=15,
        )

        self._txt_aktywo = tk.Text(kolumny, **wspolne)
        self._txt_aktywo.grid(row=0, column=0, sticky="nsew")

        self._txt_benchmark = tk.Text(kolumny, **wspolne)
        self._txt_benchmark.grid(row=0, column=1, sticky="nsew")

    # ── Pomocnicze metody budowania widgetów ──────────────────────────────────

    def _pole_formularza(self, rodzic: tk.Widget, etykieta: str,
                          placeholder: str, zmienna: tk.StringVar,
                          typ: str = "text") -> None:
        """Tworzy pole tekstowe (Entry) z etykietą i podpowiedzią."""
        ramka = tk.Frame(rodzic, bg=COLORS["bg_medium"])
        ramka.pack(fill="x", pady=(5, 0))

        tk.Label(ramka, text=etykieta,
                 bg=COLORS["bg_medium"], fg=COLORS["text_secondary"],
                 font=("Courier", 8, "bold")).pack(anchor="w")

        tk.Entry(
            ramka,
            textvariable=zmienna,
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["accent_blue"],
            relief="flat",
            font=("Courier", 11),
            bd=6,
        ).pack(fill="x", ipady=2)

        tk.Label(ramka, text=placeholder,
                 bg=COLORS["bg_medium"], fg=COLORS["text_muted"],
                 font=("Courier", 7)).pack(anchor="w")

    def _lista_rozwijalna(self, rodzic: tk.Widget, etykieta: str,
                           zmienna: tk.StringVar, opcje: list[str]) -> None:
        """Tworzy listę rozwijalną (Combobox) z ciemnym motywem i etykietą."""
        ramka = tk.Frame(rodzic, bg=COLORS["bg_medium"])
        ramka.pack(fill="x", pady=(5, 0))

        tk.Label(ramka, text=etykieta,
                 bg=COLORS["bg_medium"], fg=COLORS["text_secondary"],
                 font=("Courier", 8, "bold")).pack(anchor="w")

        # Wymuszenie ciemnego motywu dla pop-upu Combobox
        self.winfo_toplevel().option_add("*TCombobox*Listbox.background", COLORS["bg_light"])
        self.winfo_toplevel().option_add("*TCombobox*Listbox.foreground", COLORS["text_primary"])
        self.winfo_toplevel().option_add("*TCombobox*Listbox.selectBackground", COLORS["accent_blue"])
        self.winfo_toplevel().option_add("*TCombobox*Listbox.selectForeground", COLORS["bg_dark"])
        self.winfo_toplevel().option_add("*TCombobox*Listbox.font", ("Courier", 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TCombobox",
                         fieldbackground=COLORS["bg_light"],
                         background=COLORS["bg_light"],
                         foreground=COLORS["text_primary"],
                         selectbackground=COLORS["accent_blue"],
                         selectforeground=COLORS["bg_dark"],
                         bordercolor=COLORS["border"],
                         darkcolor=COLORS["bg_light"],
                         lightcolor=COLORS["bg_light"],
                         arrowcolor=COLORS["accent_blue"],
                         arrowsize=12)
        style.map("Dark.TCombobox",
                  fieldbackground=[("readonly", COLORS["bg_light"]),
                                   ("focus", COLORS["bg_light"])],
                  foreground=[("readonly", COLORS["text_primary"])],
                  background=[("readonly", COLORS["bg_light"])],
                  arrowcolor=[("readonly", COLORS["accent_blue"]),
                               ("pressed", COLORS["text_primary"])])

        ttk.Combobox(ramka, textvariable=zmienna, values=opcje,
                     state="readonly", style="Dark.TCombobox",
                     font=("Courier", 10)).pack(fill="x", ipady=4)

    # ── API publiczne ─────────────────────────────────────────────────────────

    def zaktualizuj_metryki(self, metryki_aktywa: dict,
                             metryki_benchmark: dict | None) -> None:
        """
        Aktualizuje wyświetlane metryki po zakończeniu analizy.

        Args:
            metryki_aktywa:    Słownik metryk głównego instrumentu.
            metryki_benchmark: Słownik metryk benchmarku lub None.
        """
        def fmt_usd(v: float) -> str:
            return f"${v:,.2f}"

        def fmt_proc(v: float) -> str:
            return f"{'+'if v >= 0 else ''}{v:.1f}%"

        def blok(m: dict) -> str:
            return (
                f"{m['nazwa']}\n"
                f"Zainwest: {fmt_usd(m['zainwestowano'])}\n"
                f"Wart.koń: {fmt_usd(m['wartosc_koncowa'])}\n"
                f"Zysk/Str: {fmt_usd(m['zysk'])}\n"
                f"Zwrot:    {fmt_proc(m['zwrot_proc'])}\n"
                f"CAGR:     {fmt_proc(m['cagr'])}\n"
                f"Max DD:   {m['max_drawdown']:.1f}%"
            )

        self._ustaw_tekst(self._txt_aktywo, blok(metryki_aktywa))
        self._ustaw_tekst(
            self._txt_benchmark,
            blok(metryki_benchmark) if metryki_benchmark else "",
        )

    def ustaw_stan_przycisku(self, stan: str, tekst: str) -> None:
        """Zmienia stan i etykietę przycisku 'Analizuj'."""
        self.btn_analizuj.config(state=stan, text=tekst)

    # ── Metody prywatne ───────────────────────────────────────────────────────

    @staticmethod
    def _ustaw_tekst(widget: tk.Text, tekst: str) -> None:
        """Pomocnik: zapisuje tekst do wyłączonego widgetu Text."""
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", tekst)
        widget.config(state="disabled")
