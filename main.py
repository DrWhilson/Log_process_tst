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


if __name__ == "__main__":
    # Параметры
    parser = argparse.ArgumentParser(description="Генератор отчётов")

    parser.add_argument(
        "--file",
        nargs="+",
        required=True,
        type=str,
        help="Путь к файлу с данными (обязательно)",
    )
    parser.add_argument(
        "--report",
        type=str,
        default="average",
        help="Отчёт по полю (по умолчанию: average)",
    )

    args = parser.parse_args()

    # Загрузка данных
    log = load_mult_log(args.file)

    # Обработка данных
    group_data = defaultdict(lambda: {"sum": 0, "count": 0})

    for item in log:
        urlClass = item["url"]
        vag = item["response_time"]
        group_data[urlClass]["sum"] += vag
        group_data[urlClass]["count"] += 1

    result = [
        {"url": url, "average_vag": data["sum"] / data["count"], "count": data["count"]}
        for url, data in group_data.items()
    ]

    # Вывод отчёта
    header = ["", "hander", "total", "average_vag"]
    body = []
    for index, urlClass in enumerate(result):
        row = [index]
        row.append(urlClass["url"])
        row.append(urlClass["count"])
        row.append(round(urlClass["average_vag"], 3))
        body.append(row)

    print(tabulate(body, header, tablefmt="grid"))
