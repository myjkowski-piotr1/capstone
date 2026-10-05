import argparse
import csv
import json
from collections import Counter
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "sales.csv"
DEFAULT_CONFIG = PROJECT_ROOT / "data" / "config.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "daily_summary.csv"
REQUIRED_COLUMNS = {"date", "product", "units", "unit_price", "region"}
REPORT_COLUMNS = {
    "generated_at": "wygenerowano_utc",
    "total_orders": "liczba_zamowien",
    "total_revenue": "laczny_przychod",
    "average_order_value": "srednia_wartosc_zamowienia",
    "top_product": "najpopularniejszy_produkt",
    "top_region": "region_z_najwieksza_liczba_zamowien",
    "threshold": "prog_przychodu",
    "orders_above_threshold": "liczba_zamowien_spelniajacych_prog",
}


def load_sales(path: Path) -> list[dict[str, Any]]:
    """Wczytuje i oczyszcza zamówienia z CSV; błędy wskazuje numerem wiersza."""
    with path.open("r", newline="", encoding="utf-8-sig") as sales_file:
        reader = csv.DictReader(sales_file)
        if not reader.fieldnames:
            raise ValueError(f"{path}: plik CSV jest pusty albo nie zawiera nagłówka")

        columns = set(reader.fieldnames)
        missing_columns = REQUIRED_COLUMNS - columns
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"{path}: brakuje wymaganych kolumn: {missing}")

        orders = []
        for line_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"{path}: za dużo wartości w wierszu {line_number}")
            if not row or all(not (value or "").strip() for value in row.values()):
                continue

            cleaned = {key: (value or "").strip() for key, value in row.items() if key}
            try:
                order_date = date.fromisoformat(cleaned["date"])
                units = int(cleaned["units"])
                unit_price = Decimal(cleaned["unit_price"])
            except (KeyError, ValueError, InvalidOperation) as error:
                raise ValueError(f"{path}: nieprawidłowe dane zamówienia w wierszu {line_number}") from error

            if not cleaned.get("product") or not cleaned.get("region"):
                raise ValueError(f"{path}: produkt i region są wymagane w wierszu {line_number}")
            if units <= 0 or not unit_price.is_finite() or unit_price < 0:
                raise ValueError(
                    f"{path}: liczba sztuk musi być dodatnia, a cena nieujemna (wiersz {line_number})"
                )

            orders.append(
                {
                    "date": order_date,
                    "product": cleaned["product"],
                    "units": units,
                    "unit_price": unit_price,
                    "region": cleaned["region"],
                }
            )
        return orders


def load_config(path: Path) -> Decimal:
    """Wczytuje z JSON i sprawdza minimalny próg przychodu dla zamówienia."""
    with path.open("r", encoding="utf-8-sig") as config_file:
        config = json.load(config_file)
    if not isinstance(config, dict):
        raise ValueError(f"{path}: konfiguracja JSON musi być obiektem")
    try:
        threshold = Decimal(str(config["threshold"]))
    except (KeyError, InvalidOperation) as error:
        raise ValueError(f"{path}: wartość 'threshold' musi być prawidłową liczbą") from error
    if not threshold.is_finite() or threshold < 0:
        raise ValueError(f"{path}: wartość 'threshold' musi być nieujemną liczbą")
    return threshold


def create_report(orders: list[dict[str, Any]], threshold: Decimal) -> dict[str, str | int]:
    """Oblicza dzienne podsumowanie na podstawie sprawdzonych zamówień."""
    product_units = Counter()
    region_orders = Counter()
    total_revenue = Decimal("0")
    orders_above_threshold = 0

    for order in orders:
        order_revenue = order["units"] * order["unit_price"]
        total_revenue += order_revenue
        product_units[order["product"]] += order["units"]
        region_orders[order["region"]] += 1
        orders_above_threshold += order_revenue >= threshold

    # Sortowanie nazw zapewnia powtarzalny wynik, gdy kilka pozycji ma taki sam wynik.
    top_product = min(product_units, key=lambda name: (-product_units[name], name)) if product_units else "n/a"
    top_region = min(region_orders, key=lambda name: (-region_orders[name], name)) if region_orders else "n/a"

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_orders": len(orders),
        "total_revenue": f"{total_revenue:.2f}",
        "average_order_value": f"{total_revenue / len(orders):.2f}" if orders else "0.00",
        "top_product": top_product,
        "top_region": top_region,
        "threshold": f"{threshold:.2f}",
        "orders_above_threshold": orders_above_threshold,
    }


def write_report(report: dict[str, str | int], path: Path) -> None:
    """Zapisuje podsumowanie i tworzy folder docelowy, jeśli jeszcze nie istnieje."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as report_file:
        writer = csv.DictWriter(report_file, fieldnames=REPORT_COLUMNS.values())
        writer.writeheader()
        writer.writerow({REPORT_COLUMNS[key]: value for key, value in report.items()})


def main() -> None:
    parser = argparse.ArgumentParser(description="Tworzy podsumowanie sprzedaży z pliku CSV.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Ścieżka do pliku CSV ze sprzedażą.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Ścieżka do konfiguracji raportu w JSON.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Ścieżka do wynikowego pliku CSV.")
    args = parser.parse_args()

    try:
        orders = load_sales(args.input)
        threshold = load_config(args.config)
        report = create_report(orders, threshold)
        write_report(report, args.output)
    except FileNotFoundError as error:
        parser.error(f"nie znaleziono pliku: {error.filename}")
    except (OSError, UnicodeError, csv.Error, json.JSONDecodeError, ValueError) as error:
        parser.error(str(error))
    print(
        f"Utworzono raport {args.output}: zamówienia={report['total_orders']}, "
        f"przychód={report['total_revenue']}."
    )


if __name__ == "__main__":
    main()
