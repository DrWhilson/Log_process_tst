import pytest
import os
import json
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile

from log_gen import (
    load_log,
    load_mult_log,
    apply_filter,
    group_log,
    calc_report_values,
    form_report,
)


@pytest.fixture
def sample_log_data():
    return [
        {
            "@timestamp": "2023-01-01T12:00:00",
            "url": "/home",
            "response_time": 0.5,
            "http_user_agent": "Chrome",
        },
        {
            "@timestamp": "2023-01-01T12:01:00",
            "url": "/about",
            "response_time": 0.8,
            "http_user_agent": "Firefox",
        },
        {
            "@timestamp": "2023-01-02T12:00:00",
            "url": "/home",
            "response_time": 0.6,
            "http_user_agent": "Chrome",
        },
        {
            "@timestamp": "2023-01-03T12:00:00",
            "url": "/contact",
            "response_time": 1.0,
            "http_user_agent": "Safari",
        },
    ]


@pytest.fixture
def temp_log_file(sample_log_data):
    with NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
        for item in sample_log_data:
            f.write(json.dumps(item) + "\n")
        f.flush()
        yield f.name
    os.unlink(f.name)


def test_load_log(temp_log_file, sample_log_data):
    loaded_data = load_log(temp_log_file)
    assert len(loaded_data) == len(sample_log_data)
    assert loaded_data[0]["url"] == "/home"
    assert loaded_data[1]["response_time"] == 0.8

    loaded_data = load_log("wrong_file")
    assert loaded_data == []


def test_load_mult_log(temp_log_file):
    with NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f2:
        f2.write(
            json.dumps({"@timestamp": "2023-01-04T12:00:00", "url": "/new"}) + "\n"
        )
        f2.flush()

        loaded_data = load_mult_log([temp_log_file, f2.name])
        assert len(loaded_data) == 5
        assert loaded_data[-1]["url"] == "/new"

        loaded_data = load_mult_log([temp_log_file, "nonexistent_file.log"])
        assert len(loaded_data) == 4
    os.unlink(f2.name)


def test_apply_filter(sample_log_data):
    filtered = apply_filter(sample_log_data, "2023-01-01")
    assert len(filtered) == 2
    assert all("2023-01-01" in item["@timestamp"] for item in filtered)

    filtered = apply_filter(sample_log_data, "2023-01-01/2023-01-02")
    assert len(filtered) == 3

    filtered = apply_filter(sample_log_data, "2022-12-20/2023-01-02")
    assert len(filtered) == 3

    filtered = apply_filter(sample_log_data, "2023-01-01/2023-01-20")
    assert len(filtered) == 4

    filtered = apply_filter(sample_log_data, "2022-12-20/2023-01-20")
    assert len(filtered) == 4

    filtered = apply_filter(sample_log_data, "2023-01-02/2023-01-01")
    assert len(filtered) == 4


def test_group_log(sample_log_data):
    grouped = group_log(sample_log_data, "url")
    assert len(grouped) == 3
    assert "/home" in grouped
    assert len(grouped["/home"]["response_time"]) == 2

    grouped = group_log(sample_log_data, "http_user_agent")
    assert len(grouped) == 3
    assert "Chrome" in grouped

    grouped = group_log(sample_log_data, "wrong_field")
    assert grouped == []


def test_calc_report_values(sample_log_data):
    report = calc_report_values(sample_log_data, "url", "response_time", "avg")
    assert len(report) == 3
    assert any(
        item["url"] == "/home" and item["avg_response_time"] == 0.55 for item in report
    )

    report = calc_report_values(sample_log_data, "url", "response_time", "min")
    assert any(
        item["url"] == "/home" and item["avg_response_time"] == 0.5 for item in report
    )

    report = calc_report_values(sample_log_data, "url", "response_time", "max")
    assert any(
        item["url"] == "/home" and item["avg_response_time"] == 0.6 for item in report
    )

    report = calc_report_values(sample_log_data, "url")
    assert all("avg_response_time" not in item for item in report)

    report = calc_report_values(sample_log_data, "curl")
    assert report is None

    report = calc_report_values(sample_log_data, "url", "wrong_calc_field")
    assert report is None

    report = calc_report_values(sample_log_data, "url", "response_time", "avv")
    assert report is None


def test_form_report(sample_log_data):
    report = form_report(sample_log_data, "average", "all")
    assert len(report) == 3
    assert any(item["url"] == "/home" for item in report)

    report = form_report(sample_log_data, "browser", "all")
    assert len(report) == 3
    assert any(item["http_user_agent"] == "Chrome" for item in report)

    report = form_report(sample_log_data, "average", "2023-01-01")
    assert len(report) == 2

    report = form_report(sample_log_data, "unknown", "all")
    assert report is None

    report = form_report([], "average", "all")
    assert report is None
