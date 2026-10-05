import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from report_bot import create_report, load_config, load_sales, write_report


def test_load_sales_cleans_whitespace_and_skips_blank_rows(tmp_path):
    sales_file = tmp_path / "sales.csv"
    sales_file.write_text(
        "date,product,units,unit_price,region\n"
        "2025-01-01, Widget ,2,10.50, EU-West \n"
        ",,,,\n",
        encoding="utf-8",
    )

    orders = load_sales(sales_file)

    assert orders == [
        {
            "date": date(2025, 1, 1),
            "product": "Widget",
            "units": 2,
            "unit_price": Decimal("10.50"),
            "region": "EU-West",
        }
    ]


def test_load_sales_reports_malformed_rows(tmp_path):
    sales_file = tmp_path / "sales.csv"
    sales_file.write_text(
        "date,product,units,unit_price,region\n"
        "not-a-date,Widget,2,10.50,EU-West\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="wierszu 2"):
        load_sales(sales_file)


def test_load_sales_rejects_rows_with_extra_values(tmp_path):
    sales_file = tmp_path / "sales.csv"
    sales_file.write_text(
        "date,product,units,unit_price,region\n"
        "2025-01-01,Widget,2,10.50,EU-West,unexpected\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="za dużo wartości w wierszu 2"):
        load_sales(sales_file)


def test_create_report_calculates_totals_and_stable_leaders():
    orders = [
        {"product": "Beta", "units": 2, "unit_price": Decimal("10.00"), "region": "West"},
        {"product": "Alpha", "units": 2, "unit_price": Decimal("15.00"), "region": "East"},
    ]

    report = create_report(orders, Decimal("25"))

    assert report["total_orders"] == 2
    assert report["total_revenue"] == "50.00"
    assert report["average_order_value"] == "25.00"
    assert report["top_product"] == "Alpha"
    assert report["top_region"] == "East"
    assert report["orders_above_threshold"] == 1


def test_create_report_handles_empty_data():
    report = create_report([], Decimal("85"))

    assert report["total_orders"] == 0
    assert report["total_revenue"] == "0.00"
    assert report["average_order_value"] == "0.00"
    assert report["top_product"] == "n/a"
    assert report["top_region"] == "n/a"


def test_config_and_report_are_loaded_and_written(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"threshold": 12.5}', encoding="utf-8")
    report_path = tmp_path / "reports" / "summary.csv"
    report = create_report([], load_config(config_file))

    write_report(report, report_path)

    with report_path.open(newline="", encoding="utf-8") as output:
        row = next(csv.DictReader(output))
    assert row["prog_przychodu"] == "12.50"
    assert row["liczba_zamowien"] == "0"
