import pickle
from table import Table
from exceptions import StructureMismatchError

def load_table(*files, detect_types=False):
    tables = []
    for f in files:
        with open(f, 'rb') as pf:
            obj = pickle.load(pf)
            # Предполагаем, что pickle содержит данные в формате:
            # {
            #   "columns": [...],
            #   "data": [...],
            #   "types": {col_name: type}
            # }
            columns = obj["columns"]
            data = obj["data"]
            types = obj["types"]
            t = Table(columns=columns, data=data, types=types)
            tables.append(t)

    if not tables:
        raise StructureMismatchError("Не удалось загрузить ни одной таблицы")

    # Проверим структуру
    for t in tables[1:]:
        if t.columns != tables[0].columns:
            raise StructureMismatchError("Структура столбцов не совпадает в разных файлах")

        # Проверка типов тоже
        for c in t.columns:
            if t.types[c] != tables[0].types[c]:
                raise StructureMismatchError("Типы столбцов не совпадают в разных файлах")

    # Объединим
    res = tables[0]
    for t in tables[1:]:
        res = Table.concat(res, t)

    if detect_types:
        res.detect_column_types()

    return res

def save_table(table, file_path):
    obj = {
        "columns": table.columns,
        "data": table.data,
        "types": table.types
    }
    with open(file_path, 'wb') as pf:
        pickle.dump(obj, pf)
