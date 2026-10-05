# Automatyczny raport sprzedaży

Automatyczny raport sprzedaży to skrypt w Pythonie, który analizuje zamówienia z pliku CSV i zapisuje podsumowanie sprzedaży w drugim pliku CSV.

## Problem i odbiorcy

Ręczne podsumowywanie wielu zamówień jest czasochłonne i łatwo o pomyłkę. Projekt automatyzuje obliczenia, sprawdza poprawność danych wejściowych i przygotowuje powtarzalny raport. Jest przeznaczony dla osób uczących się automatyzacji w Pythonie oraz dla małych zespołów, które chcą cyklicznie podsumowywać dane sprzedażowe.

## Funkcje

- Wczytuje zamówienia z CSV i czyści zbędne białe znaki.
- Sprawdza wymagane kolumny, daty, liczby sztuk, ceny oraz wartości wierszy.
- Oblicza liczbę zamówień, łączny przychód i średnią wartość zamówienia.
- Wskazuje najpopularniejszy produkt i region oraz liczbę zamówień spełniających próg z konfiguracji.
- Zapisuje raport CSV z polskimi nagłówkami i czytelnie zgłasza błędy danych lub plików.
- GitHub Actions uruchamia testy i generuje raport na żądanie, po zmianie kodu oraz według harmonogramu.

## Wymagania

- Python 3.12 lub nowszy.
- [uv](https://docs.astral.sh/uv/).
- Git do sklonowania repozytorium.

## Instalacja

W PowerShellu lub terminalu uruchom:

```powershell
git clone https://github.com/myjkowski-piotr1/capstone.git
cd capstone
uv sync --locked --dev
```

Polecenie `uv sync` tworzy środowisko projektu i instaluje dokładne wersje zależności zapisane w `uv.lock`.

## Uruchomienie i użycie

Aby wygenerować raport z przykładowych danych:

```powershell
uv run python src/report_bot.py
```

Domyślnie program odczytuje `data/sales.csv` i `data/config.json`, a raport zapisuje do `reports/daily_summary.csv`. Ścieżki można zmienić opcjami:

```powershell
uv run python src/report_bot.py --input data/sales.csv --config data/config.json --output reports/daily_summary.csv
```

Próg minimalnego przychodu dla zamówienia ustawia się w `data/config.json`:

```json
{
  "threshold": 85
}
```

Przykładowy komunikat po poprawnym uruchomieniu:

```text
Utworzono raport reports/daily_summary.csv: zamówienia=300, przychód=786324.77.
```

Raport zawiera również średnią wartość zamówienia, najpopularniejszy produkt i region oraz liczbę zamówień osiągających skonfigurowany próg. Dane z przykładowego pliku wejściowego mogą się zmienić, więc wartości raportu zależą od jego zawartości.

## Testy

Uruchom testy automatyczne poleceniem:

```powershell
uv run --locked pytest
```

Testy obejmują poprawne dane, przypadki brzegowe, błędy CSV i JSON, obliczenia raportu oraz obsługę argumentów programu.

## Jak to działa

```text
data/sales.csv ──┐
                 ├─> src/report_bot.py ──> reports/daily_summary.csv
data/config.json ┘             │
                               └─ walidacja i obliczenia
```

Program wczytuje i waliduje pliki wejściowe, oblicza statystyki, a następnie zapisuje wynik. Testy w `tests/test_report_bot.py` sprawdzają te zachowania. Workflow `.github/workflows/automation.yml` instaluje projekt, uruchamia testy i tworzy raport jako artefakt. Uruchamia się przy `push`, pull requestach, ręcznie oraz codziennie o 08:00 UTC.

Generator przetwarza lokalne pliki i nie wykonuje żądań sieciowych, dlatego obsługa błędów połączenia nie dotyczy jego działania. Ewentualne problemy z pobraniem kodu lub zależności w CI są widoczne w logach GitHub Actions.

## Stos technologiczny

- Python 3.12+
- `uv` do zarządzania środowiskiem i zależnościami
- `pytest` do testów automatycznych
- GitHub Actions do automatycznego testowania i generowania raportu

## Struktura projektu

```text
.
├── .github/workflows/automation.yml
├── data/
│   ├── config.json
│   └── sales.csv
├── reports/
├── src/report_bot.py
├── tests/test_report_bot.py
├── pyproject.toml
└── uv.lock
```

## Plan prac

Zadania projektu opisuje plik [PROJECT_ISSUES.md](./PROJECT_ISSUES.md), a tablica GitHub Project jest dostępna [tutaj](https://github.com/users/myjkowski-piotr1/projects/1). Zgłoszenia 1–6 są zamknięte.
