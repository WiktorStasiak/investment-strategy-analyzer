# Buy & Hold Strategy Analyzer

Aplikacja desktopowa do analizy strategii inwestycyjnej **Buy & Hold** z porównaniem do dowolnego benchmarku (domyślnie S&P 500). Dane pobierane są w czasie rzeczywistym z Yahoo Finance.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat)

---

## Zrzut ekranu

> Wprowadź ticker, ustaw parametry i kliknij **Analizuj** — wykresy aktualizują się automatycznie.

---

## Funkcje

- Symulacja strategii **Buy & Hold** z regularnym dokupowaniem (codziennie / tygodniowo / miesięcznie / kwartalnie)
- Porównanie z dowolnym benchmarkiem z Yahoo Finance (np. `^GSPC`, `QQQ`, `GLD`, `BTC-USD`)
- Interaktywne wykresy matplotlib z ciemnym motywem:
  - Wartość portfela vs zainwestowany kapitał
  - Ceny historyczne (tryb bez benchmarku) lub skumulowany zwrot % (tryb z benchmarkiem)
- Panel metryk inwestycyjnych: zysk/strata, zwrot %, CAGR, Maximum Drawdown
- Zapis wykresu do pliku PNG / PDF / SVG
- Analiza uruchamiana w wątku tła — GUI nie blokuje się podczas pobierania danych

---

## Wymagania

- Python 3.11+
- Połączenie z internetem (dane pobierane z Yahoo Finance)

---

## Instalacja

```bash
git clone https://github.com/<twoj-login>/buy-and-hold-strategy-analyzer.git
cd buy-and-hold-strategy-analyzer
pip install -r requirements.txt
python main.py
```

### requirements.txt

```
yfinance>=0.2
pandas>=2.0
numpy>=1.26
matplotlib>=3.8
```

---

## Użycie

| Pole | Opis | Przykład |
|---|---|---|
| **Ticker instrumentu** | Symbol z Yahoo Finance | `AAPL`, `MSFT`, `SPY`, `QQQ` |
| **Ticker benchmark** | Symbol do porównania (opcjonalny) | `^GSPC`, `GLD`, `BTC-USD` |
| **Kwota inwestycji** | Kwota dokupywana w każdym cyklu | `500` |
| **Okres analizy** | Horyzont czasowy | 1 / 2 / 3 / 5 / 10 / 20 lat |
| **Częstotliwość** | Jak często dokupywać | Codziennie / Co tydzień / Co miesiąc / Co kwartał |

Pole benchmarku można zostawić puste — wtedy dolny wykres pokazuje same ceny historyczne zamiast porównania zwrotów.

---

## Struktura projektu

```
buy-and-hold-strategy-analyzer/
├── main.py                 # Punkt wejścia
├── config.py               # Stałe: kolory, opcje częstotliwości i okresów
├── requirements.txt
├── data/
│   ├── fetcher.py          # Pobieranie danych z Yahoo Finance (yfinance)
│   └── analyzer.py         # Symulacja portfela i obliczanie metryk
└── ui/
    ├── app.py              # Główna klasa okna — koordynacja i walidacja
    ├── left_panel.py       # Panel formularza i wyników (LeftPanel)
    └── chart_panel.py      # Panel wykresów matplotlib (ChartPanel)
```

Warstwy są oddzielone — `data/` nie importuje niczego z `ui/`, zależności płyną tylko w jedną stronę.

---

## Metryki inwestycyjne

| Metryka | Opis |
|---|---|
| **Zwrot %** | `(wartość końcowa − zainwestowano) / zainwestowano × 100` |
| **CAGR** | Uproszczona średnioroczna stopa wzrostu: `(końcowa / wejście)^(1/n) − 1` |
| **Maximum Drawdown** | Największy szczyt-do-dołka spadek wartości portfela w % |

> CAGR liczony jest na podstawie łącznej zainwestowanej kwoty, nie pierwszej wpłaty — jest to uproszczenie właściwe dla strategii DCA (Dollar-Cost Averaging).

---

## Licencja

MIT — szczegóły w pliku [LICENSE](LICENSE).
