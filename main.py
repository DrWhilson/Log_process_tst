import os
import json
import argparse
import tabulate


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
    data = load_mult_log(args.file)

    # Обработка данных
    print(len(data))
