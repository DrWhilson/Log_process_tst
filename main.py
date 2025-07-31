import os
import json
import argparse
from collections import defaultdict

from tabulate import tabulate


def load_log(path):
    data = []
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            data.append(json.loads(line.strip()))

    return data


def load_mult_log(files):
    data = []
    for file_path in files:
        if not os.path.exists(file_path):
            print(f"Файл {file_path} не найден")
            continue
        file_data = load_log(file_path)
        data.extend(file_data)

    return data


def apply_filter(data, date_filter):
    return [item for item in data if date_filter in item["@timestamp"]]


def calc_reprt(data, search_param, date_filter):
    if date_filter != "all":
        data = apply_filter(data, date_filter)

    group_data = defaultdict(lambda: {"sum": 0, "count": 0})

    for item in data:
        urlClass = item["url"]
        vag = item["response_time"]
        group_data[urlClass]["sum"] += vag
        group_data[urlClass]["count"] += 1

    result = [
        {
            "url": url,
            "avg_response_time": data["sum"] / data["count"],
            "count": data["count"],
        }
        for url, data in group_data.items()
    ]

    return result


def print_table(header, data, dict):
    data = []
    for index, urlClass in enumerate(dict):
        row = [index]
        for key in body:
            row.append(urlClass[key])
        data.append(row)

    print(tabulate(data, header, tablefmt="grid"))


if __name__ == "__main__":
    # Параметры
    parser = argparse.ArgumentParser(description="Генератор отчётов")

    parser.add_argument(
        "--file",
        nargs="+",
        required=True,
        type=str,
        help="Путь к файлам с данными (обязательно)",
    )
    parser.add_argument(
        "--report",
        type=str,
        default="average",
        help="Отчёт по полю (по умолчанию: average)",
    )
    parser.add_argument(
        "--date",
        type=str,
        default="all",
        help="Фильтр по дате (по умолчанию: all)",
    )

    args = parser.parse_args()

    # Загрузка данных
    log = load_mult_log(args.file)

    # Обработка данных
    report = calc_reprt(log, args.report, args.date)

    # Вывод отчёта
    header = ["", "hander", "total", "avg_response_time"]
    body = ["url", "count", "avg_response_time"]
    print_table(header, body, report)
