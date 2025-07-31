import json
import argparse
import tabulate

parser = argparse.ArgumentParser(description="Генератор отчётов")

parser.add_argument(
    "--file",
    required=True,
    type=str,
    help="Путь к файлу с данными (обязательно)"
)
parser.add_argument(
    "--report",
    type=str,
    default="average",
    help="Отчёт по полю (по умолчанию: average)"
)

args = parser.parse_args()


data = []
with open('example1.log', 'r', encoding='utf-8') as file:
    for line in file:
        data.append(json.loads(line.strip()))

for i in range(len(data)):
    print(data[i])
