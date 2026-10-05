import csv
import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from report_bot import create_report, load_config, load_sales, main, write_report


def test_load_sales_reports_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_sales(tmp_path / "missing.csv")


def test_load_sales_reports_empty_file(tmp_path):
    sales_file = tmp_path / "empty.csv"
    sales_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="plik CSV jest pusty"):
        load_sales(sales_file)


def test_load_sales_accepts_header_without_orders(tmp_path):
    sales_file = tmp_path / "no-orders.csv"
    sales_file.write_text("date,product,units,unit_price,region\n", encoding="utf-8")

    assert load_sales(sales_file) == []


def test_load_config_reports_invalid_json(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"threshold": ', encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        load_config(config_file)


def test_load_config_rejects_non_object_json(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('["not", "an", "object"]', encoding="utf-8")

    with pytest.raises(ValueError, match="musi być obiektem"):
        load_config(config_file)


def test_main_prints_actionable_error_for_missing_input(tmp_path, monkeypatch, capsys):
    missing_file = tmp_path / "missing.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        ["report_bot.py", "--input", str(missing_file)],
    )

    with pytest.raises(SystemExit) as error:
        main()

    assert error.value.code == 2
    assert str(missing_file) in capsys.readouterr().err


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
