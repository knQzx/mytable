import csv
from table import Table
from exceptions import StructureMismatchError

def load_table(*files, detect_types=False):
    # Загрузка CSV из нескольких файлов и объединение.
    # Предполагается, что все имеют одинаковые столбцы.
    tables = []
    for f in files:
        with open(f, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            if not rows:
                raise StructureMismatchError("Файл пустой или некорректный")
            columns = rows[0]
            data = rows[1:]
            t = Table(columns=columns, data=data)
            tables.append(t)

    if not tables:
        raise StructureMismatchError("Не удалось загрузить ни одной таблицы")

    # Проверим структуру
    for t in tables[1:]:
        if t.columns != tables[0].columns:
            raise StructureMismatchError("Структура столбцов не совпадает в разных файлах")

    # Объединим
    res = tables[0]
    for t in tables[1:]:
        res = Table.concat(res, t)

    # Опционально определить типы
    if detect_types:
        res.detect_column_types()

    return res

def save_table(table, file_path):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(table.columns)
        for row in table.data:
            writer.writerow(row)
