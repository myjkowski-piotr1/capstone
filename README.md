# Automatyczny raport sprzedaży

Projekt **Automatyczny raport sprzedaży** odczytuje przykładowy plik CSV z zamówieniami, oczyszcza i sprawdza dane, a następnie tworzy dzienne podsumowanie sprzedaży. Raport zawiera liczbę zamówień, łączny przychód, średnią wartość zamówienia, produkt z największą liczbą sprzedanych sztuk, region z największą liczbą zamówień oraz liczbę zamówień spełniających skonfigurowany próg przychodu. GitHub Actions może generować raport codziennie lub na żądanie.

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
└── .gitignore
```

## Uruchomienie lokalne

Zainstaluj [uv](https://docs.astral.sh/uv/) oraz Python w wersji 3.12 lub nowszej, a następnie uruchom:

```powershell
uv sync --dev
uv run python src/report_bot.py
```

Raport zostanie zapisany w `reports/daily_summary.csv`; jego nagłówki są po polsku. Ścieżki do danych wejściowych, konfiguracji i raportu można zmienić za pomocą opcji `--input`, `--config` i `--output`.

Testy uruchomisz poleceniem:

```powershell
uv run pytest
```

## Automatyzacja

Workflow GitHub Actions uruchamia się codziennie o 08:00 UTC i można go też uruchomić ręcznie w zakładce Actions. Przy każdym uruchomieniu workflow wykonuje testy i udostępnia wygenerowany plik CSV jako artefakt.

## Plan prac

Zgłoszenia z listą zadań są w pliku [PROJECT_ISSUES.md](./PROJECT_ISSUES.md), a prawdziwa tablica GitHub Project jest dostępna [tutaj](https://github.com/users/myjkowski-piotr1/projects/1). Zadania 1–4 są zamknięte, a zadanie 5 pozostaje w trakcie weryfikacji automatyzacji GitHub Actions.
