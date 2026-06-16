"""
Prawy panel interfejsu graficznego aplikacji Buy & Hold Strategy Analyzer.

Zawiera wykres matplotlib z dwoma subplotami:
    - Górny: wartość portfela w czasie.
    - Dolny: ceny historyczne (brak benchmarku) lub skumulowany zwrot (%).
"""

import tkinter as tk
from tkinter import filedialog

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from config import COLORS


class ChartPanel(tk.Frame):
    """
    Panel wykresu matplotlib osadzony w oknie tkinter.

    Args:
        rodzic:      Widget nadrzędny tkinter.
        var_status:  StringVar do aktualizacji paska statusu.
    """

    def __init__(self, rodzic: tk.Widget, var_status: tk.StringVar, **kwargs):
        super().__init__(rodzic, bg=COLORS["bg_dark"], **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._var_status = var_status
        self._zbuduj()

    # ── Budowanie panelu ──────────────────────────────────────────────────────

    def _zbuduj(self) -> None:
        """Inicjalizuje figurę matplotlib, subploty i pasek narzędzi."""
        self.fig = Figure(figsize=(10, 7), facecolor=COLORS["bg_dark"])
        self.fig.subplots_adjust(left=0.13, right=0.95, top=0.88,
                                  bottom=0.25, hspace=0.4)

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

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        self._zbuduj_pasek_narzedzi()
        self._wyswietl_ekran_startowy()

    def _zbuduj_pasek_narzedzi(self) -> None:
        """Pasek z przyciskiem zapisu wykresu."""
        pasek = tk.Frame(self, bg=COLORS["bg_dark"], pady=4)
        pasek.grid(row=1, column=0, sticky="ew")

        btn = tk.Button(
            pasek,
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
        btn.pack(side="right", padx=10)
        btn.bind("<Enter>", lambda e: btn.config(bg=COLORS["border"],
                                                  fg=COLORS["text_primary"]))
        btn.bind("<Leave>", lambda e: btn.config(bg=COLORS["bg_light"],
                                                  fg=COLORS["text_secondary"]))

    # ── API publiczne ─────────────────────────────────────────────────────────

    def wyswietl_wyniki(
        self,
        wyniki_aktywa: pd.DataFrame,
        wyniki_benchmark: pd.DataFrame | None,
        ceny_aktywa: pd.DataFrame,
        ticker: str,
        benchmark: str,
    ) -> None:
        """
        Rysuje wykresy na podstawie obliczonych wyników strategii.

        Wykres dolny:
            - Brak benchmarku → ceny historyczne (surowe ceny zamknięcia).
            - Z benchmarkiem  → skumulowany zwrot z inwestycji (%).

        Args:
            wyniki_aktywa:    DataFrame z wynikami strategii dla głównego instrumentu.
            wyniki_benchmark: DataFrame z wynikami strategii dla benchmarku lub None.
            ceny_aktywa:      DataFrame z historycznymi cenami zamknięcia.
            ticker:           Symbol głównego instrumentu.
            benchmark:        Symbol benchmarku (pusty string = brak).
        """
        self._wyczysc_osie()

        x_min = wyniki_aktywa.index[0]
        x_max = wyniki_aktywa.index[-1]

        self._rysuj_wartosc_portfela(wyniki_aktywa, wyniki_benchmark,
                                     ticker, benchmark, x_min, x_max)

        if wyniki_benchmark is None:
            self._rysuj_ceny_historyczne(ceny_aktywa, ticker, x_min, x_max)
        else:
            self._rysuj_skumulowany_zwrot(wyniki_aktywa, wyniki_benchmark,
                                          ticker, benchmark, x_min, x_max)

        for ax in (self.ax1, self.ax2):
            ax.tick_params(axis="x", colors=COLORS["text_secondary"])

        self.canvas.draw()

    # ── Prywatne metody rysowania ─────────────────────────────────────────────

    def _wyczysc_osie(self) -> None:
        """Czyści i ujednolica styl obu osi."""
        for ax in (self.ax1, self.ax2):
            ax.clear()
            ax.set_facecolor(COLORS["bg_medium"])
            for spine in ax.spines.values():
                spine.set_color(COLORS["border"])
            ax.tick_params(colors=COLORS["text_secondary"], labelsize=8)
            ax.grid(True, color=COLORS["border"], linewidth=0.5, alpha=0.7)

    def _rysuj_wartosc_portfela(
        self,
        wyniki_aktywa: pd.DataFrame,
        wyniki_benchmark: pd.DataFrame | None,
        ticker: str,
        benchmark: str,
        x_min, x_max,
    ) -> None:
        """Górny subplot: wartość portfela w czasie (z benchmarkiem lub bez)."""
        tytul = f"Wartość portfela – {ticker}"
        if benchmark:
            tytul += f" vs {benchmark}"

        if wyniki_benchmark is not None:
            self.ax1.plot(wyniki_benchmark.index,
                          wyniki_benchmark["wartosc_portfela"],
                          color=COLORS["sp500_color"], linewidth=2,
                          label=benchmark, zorder=3)

        self.ax1.plot(wyniki_aktywa.index, wyniki_aktywa["wartosc_portfela"],
                      color=COLORS["asset_color"], linewidth=2,
                      label=ticker, zorder=4)
        self.ax1.plot(wyniki_aktywa.index, wyniki_aktywa["zainwestowano"],
                      color=COLORS["text_muted"], linewidth=1.2,
                      linestyle="--", label="Zainwestowany kapitał", zorder=2)

        self.ax1.set_xlim(x_min, x_max)
        self.ax1.set_title(tytul, color=COLORS["text_primary"], fontsize=11,
                           pad=10, fontfamily="monospace")
        self.ax1.set_ylabel("Wartość (USD)", color=COLORS["text_secondary"],
                            fontsize=8, fontfamily="monospace")
        self.ax1.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        self.ax1.legend(facecolor=COLORS["bg_dark"], edgecolor=COLORS["border"],
                        labelcolor=COLORS["text_primary"], fontsize=8)

    def _rysuj_ceny_historyczne(
        self,
        ceny_aktywa: pd.DataFrame,
        ticker: str,
        x_min, x_max,
    ) -> None:
        """Dolny subplot (tryb bez benchmarku): surowe ceny zamknięcia."""
        ceny = ceny_aktywa["Close"].values
        self.ax2.plot(ceny_aktywa.index, ceny,
                      color=COLORS["asset_color"], linewidth=1.5,
                      label=f"{ticker} – cena zamknięcia", zorder=4)
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
        self.ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        self.ax2.legend(facecolor=COLORS["bg_dark"], edgecolor=COLORS["border"],
                        labelcolor=COLORS["text_primary"], fontsize=8)

    def _rysuj_skumulowany_zwrot(
        self,
        wyniki_aktywa: pd.DataFrame,
        wyniki_benchmark: pd.DataFrame,
        ticker: str,
        benchmark: str,
        x_min, x_max,
    ) -> None:
        """Dolny subplot (tryb z benchmarkiem): skumulowany zwrot (%)."""
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

    def _wyswietl_ekran_startowy(self) -> None:
        """Wyświetla ekran powitalny przed uruchomieniem pierwszej analizy."""
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

    def _zapisz_wykres(self) -> None:
        """Otwiera dialog zapisu i zapisuje bieżący wykres do pliku PNG/PDF/SVG."""
        sciezka = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg")],
            title="Zapisz wykres",
            initialfile="wykres_inwestycji",
        )
        if sciezka:
            self.fig.savefig(sciezka, dpi=150, bbox_inches="tight",
                             facecolor=self.fig.get_facecolor())
            self._var_status.set(f"✓ Wykres zapisany: {sciezka}")
