import os

import json
import argparse
from collections import defaultdict
from datetime import datetime, timedelta

from tabulate import tabulate


def load_log(path):
    if not os.path.exists(path):
        print(f"Файл {path} не найден")
        return []

    with open(path, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file]


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

    if not "/" in date_filter:
        return [item for item in data if date_filter in item["@timestamp"]]
    else:
        start, stop = date_filter.split("/")
        start = datetime.fromisoformat(start)
        stop = (
            datetime.fromisoformat(stop)
            + timedelta(days=1)
            - timedelta(microseconds=1)  # включаем границу по часам
        )

        if stop < start:
            print("Диапазон дат необходимо указывать от большего к меньшему")
            return data

        return [
            item
            for item in data
            if start
            <= datetime.fromisoformat(item["@timestamp"]).replace(tzinfo=None)
            <= stop
        ]


def group_log(data, group_key):
    group_data = defaultdict(lambda: defaultdict(list))

    if group_key not in data[0]:
        print(f"Ключь {group_key} для группировки не найден в данных")
        return []

    for item in data:
        group_value = item[group_key]

        for key, value in item.items():
            if key != group_key:
                group_data[group_value][key].append(value)
    return group_data


def calc_report_values(data, group="url", search_param="none", method="avg"):
    # Группируем лог по одному полю
    group_data = group_log(data, group)

    result = []

    # Считаем отчёт по группам
    for group_key, values in group_data.items():
        item_result = {
            group: group_key,
            "count": len(values[next(iter(values))]) if values else 0,
        }

        if search_param != "none":
            param_values = values[search_param]
            # Рассчёт по необходимой функции
            match method:
                case "avg":
                    item_result[f"avg_{search_param}"] = sum(param_values) / len(
                        param_values
                    )
                case "min":
                    item_result[f"avg_{search_param}"] = min(param_values)
                case "max":
                    item_result[f"avg_{search_param}"] = max(param_values)

        result.append(item_result)

    return result


def form_report(data, search_param, date_filter):
    if date_filter != "all":
        data = apply_filter(data, date_filter)

    if data == []:
        return None

    match search_param:
        case "average":
            return calc_report_values(data, "url", "response_time", "avg")
        case "browser":
            return calc_report_values(data, "http_user_agent")
        case _:
            return None


def print_table(header, report):
    table_data = [
        [index] + list(g_class.values()) for index, g_class in enumerate(report)
    ]
    print(tabulate(table_data, header, tablefmt="grid"))


def main():
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
        help="Фильтр по дате формат записи Y-M-D/Y-M-D или T-M-D для обного дня (по умолчанию: all)",
    )

    args = parser.parse_args()

    # Загрузка данных
    log = load_mult_log(args.file)

    # Обработка данных
    report = form_report(log, args.report, args.date)

    # Вывод отчёта
    if report == None:
        print("Произошла ошибка")
        exit()

    header = ["", "group", "total"]
    if [len(report[0].keys())]:
        header.append("calc_param")
    print_table(header, report)


if __name__ == "__main__":
    main()
