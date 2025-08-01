import os
import json
import argparse
from collections import defaultdict

from tabulate import tabulate


def load_log(path):
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
    return [item for item in data if date_filter in item["@timestamp"]]


def group_log(data, group_key):
    group_data = defaultdict(lambda: defaultdict(list))

    for item in data:
        group_value = item[group_key]

        keys_list = [k for k in item.keys() if k != group_key]

        for key in keys_list:
            group_data[group_value][key].append(item[key])
    return group_data


def calc_report_values(data, group="url", search_param="none", method="avg"):
    # Группируем лог по одному полю
    group_data = group_log(data, group)

    result = []

    # Считаем отчёт по группам
    for group_key, values in group_data.items():
        item_result = {group: group_key, "count": len(values[next(iter(values))])}

        if search_param != "none":
            match method:
                case "avg":
                    item_result[f"avg_{search_param}"] = sum(
                        values[search_param]
                    ) / len(values[search_param])
                case "min":
                    item_result[f"avg_{search_param}"] = min(values[search_param])
                case "max":
                    item_result[f"avg_{search_param}"] = max(values[search_param])

        result.append(item_result)

    return result


def form_report(data, search_param, date_filter):
    if date_filter != "all":
        data = apply_filter(data, date_filter)

    result = None
    match search_param:
        case "average":
            result = calc_report_values(data, "url", "response_time", "avg")
        case "browser":
            result = calc_report_values(data, "http_user_agent")

    return result


def print_table(header, report):
    table_data = []
    for index, g_class in enumerate(report):
        row = [index]
        for keys in g_class:
            row.append(g_class[keys])
        table_data.append(row)

    print(tabulate(table_data, header, tablefmt="grid"))


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
    report = form_report(log, args.report, args.date)

    # Вывод отчёта
    header = ["", "group", "total"]
    if [len(report[0].keys())]:
        header.append("calc_param")
    print_table(header, report)
