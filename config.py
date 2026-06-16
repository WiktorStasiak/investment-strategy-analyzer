"""
Stałe konfiguracyjne aplikacji Investment Analyzer.
Zawiera: domyślny ticker benchmarku, opcje częstotliwości/okresu oraz paletę kolorów.
"""

SP500_TICKER = "^GSPC"

FREQUENCY_OPTIONS: dict[str, str] = {
    "Codziennie": "D",
    "Co tydzień": "W",
    "Co miesiąc": "ME",
    "Co kwartał": "QE",
}

PERIOD_OPTIONS: dict[str, int] = {
    "1 rok": 1,
    "2 lata": 2,
    "3 lata": 3,
    "5 lat": 5,
    "10 lat": 10,
    "20 lat": 20,
}

# Paleta kolorów aplikacji (ciemny motyw finansowy)
COLORS: dict[str, str] = {
    "bg_dark":       "#0d1117",
    "bg_medium":     "#161b22",
    "bg_light":      "#21262d",
    "border":        "#30363d",
    "accent_blue":   "#58a6ff",
    "accent_green":  "#3fb950",
    "accent_red":    "#f85149",
    "accent_gold":   "#e3b341",
    "text_primary":  "#f0f6fc",
    "text_secondary":"#8b949e",
    "text_muted":    "#484f58",
    "sp500_color":   "#e3b341",
    "asset_color":   "#58a6ff",
}
