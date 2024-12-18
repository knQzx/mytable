from copy import deepcopy
from exceptions import (StructureMismatchError, InvalidColumnError, 
                         InvalidRowError, TypeConversionError, BoolListLengthError,
                         MergeConflictError)
import math

class Table:
    def __init__(self, columns=None, data=None, types=None):
        # columns - список названий столбцов
        # data - список списков значений
        # types - словарь {имя_столбца: тип_значений} или {номер_столбца: тип_значений}
        if columns is None:
            columns = []
        if data is None:
            data = []
        self.columns = columns
        self.data = data
        # Типы столбцов хранятся в виде словаря по именам столбцов
        # По умолчанию все типы строковые
        if types is None:
            self.types = {col: str for col in self.columns}
        else:
            # Если types даны по номерам
            # либо сразу по именам, нужно привести к виду имен
            if all(isinstance(k, int) for k in types.keys()):
                # сопоставим номера с именами
                new_types = {}
                for i, col in enumerate(self.columns):
                    if i in types:
                        new_types[col] = types[i]
                    else:
                        new_types[col] = str
                self.types = new_types
            else:
                self.types = types

    def _check_column(self, column, by_number=False):
        if by_number:
            if not (0 <= column < len(self.columns)):
                raise InvalidColumnError("Неверный индекс столбца")
            col_name = self.columns[column]
        else:
            if column not in self.columns:
                raise InvalidColumnError(f"Столбец {column} не найден")
            col_name = column
        return col_name

    def _convert_value(self, value, t):
        # Преобразуем значение к типу t
        if t == int:
            return int(value)
        elif t == float:
            return float(value)
        elif t == bool:
            # Считаем истиной непустую строку "True" и ненулевые числа
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes")
            return bool(value)
        elif t == str:
            return str(value)
        else:
            return value

    def _convert_column(self, column_name, to_type):
        # Преобразовать столбец к указанному типу
        col_index = self.columns.index(column_name)
        for i in range(len(self.data)):
            try:
                self.data[i][col_index] = self._convert_value(self.data[i][col_index], to_type)
            except ValueError:
                raise TypeConversionError(f"Не удалось преобразовать значение {self.data[i][col_index]} к типу {to_type}")
        self.types[column_name] = to_type

    def print_table(self):
        # Печать таблицы
        print(" | ".join(self.columns))
        print("-" * (3 * len(self.columns)))
        for row in self.data:
            print(" | ".join(str(x) for x in row))

    def get_rows_by_number(self, start, stop=None, copy_table=False):
        # Возвращает подтаблицу по номерам строк [start:stop] или [start] если stop=None
        if stop is None:
            # одна строка
            if not (0 <= start < len(self.data)):
                raise InvalidRowError("Индекс строки вне диапазона")
            new_data = [self.data[start]]
        else:
            if not (0 <= start < len(self.data)):
                raise InvalidRowError("Начальный индекс строки вне диапазона")
            if not (0 <= stop <= len(self.data)):
                raise InvalidRowError("Конечный индекс строки вне диапазона")
            new_data = self.data[start:stop]

        if copy_table:
            new_table = Table(columns=deepcopy(self.columns), data=deepcopy(new_data), types=deepcopy(self.types))
        else:
            # Не копируем, а представляем ту же память
            # Можно просто создать новый объект Table с теми же данными, но
            # тогда изменения будут видны в исходной. Для этого передадим не deepcopy
            # а прямую ссылку. Но чтобы не испортить self.columns/self.types,
            # их можно оставить теми же (они неизменны)
            new_table = Table(columns=self.columns, data=new_data, types=self.types)
        return new_table

    def get_rows_by_index(self, *vals, copy_table=False):
        # Возвращает строки, у которых в первом столбце значения совпадают с переданными.
        # Первый столбец - self.columns[0].
        if not self.columns:
            raise InvalidColumnError("Нет столбцов в таблице")
        first_col_index = 0
        selected = []
        for row in self.data:
            if row[first_col_index] in vals:
                selected.append(row)
        if copy_table:
            return Table(columns=deepcopy(self.columns), data=deepcopy(selected), types=deepcopy(self.types))
        else:
            return Table(columns=self.columns, data=selected, types=self.types)

    def get_column_types(self, by_number=True):
        # Возвращает словарь {номер_столбца: тип} или {имя_столбца: тип}
        if by_number:
            return {i: self.types[col] for i, col in enumerate(self.columns)}
        else:
            return dict(self.types)

    def set_column_types(self, types_dict, by_number=True):
        # Задает типы столбцов и конвертирует данные
        if by_number:
            # types_dict - ключи индексы столбцов
            for i, t in types_dict.items():
                if not (0 <= i < len(self.columns)):
                    raise InvalidColumnError("Неверный индекс столбца в types_dict")
                col_name = self.columns[i]
                self._convert_column(col_name, t)
        else:
            # types_dict - ключи имена столбцов
            for col_name, t in types_dict.items():
                if col_name not in self.columns:
                    raise InvalidColumnError(f"Столбец {col_name} не найден")
                self._convert_column(col_name, t)

    def get_values(self, column=0):
        # Получить список значений для столбца
        if isinstance(column, int):
            col_name = self._check_column(column, by_number=True)
        else:
            col_name = self._check_column(column, by_number=False)
        col_index = self.columns.index(col_name)
        return [self.data[i][col_index] for i in range(len(self.data))]

    def get_value(self, column=0):
        # Для таблицы из одной строки возвращает одно значение
        if len(self.data) != 1:
            raise InvalidRowError("Таблица содержит не одну строку")
        return self.get_values(column=column)[0]

    def set_values(self, values, column=0):
        # Установить список значений в столбец
        if len(values) != len(self.data):
            raise InvalidRowError("Длина списка значений не совпадает с количеством строк")
        if isinstance(column, int):
            col_name = self._check_column(column, by_number=True)
        else:
            col_name = self._check_column(column, by_number=False)
        col_index = self.columns.index(col_name)
        t = self.types[col_name]
        for i, v in enumerate(values):
            self.data[i][col_index] = self._convert_value(v, t)

    def set_value(self, value, column=0):
        # Для таблицы с одной строкой установить одно значение
        if len(self.data) != 1:
            raise InvalidRowError("Таблица содержит не одну строку")
        self.set_values([value], column=column)

    def detect_column_types(self):
        # Автоматическое определение типа столбцов по их значениям
        # Алгоритм: попробуем привести все значения столбца к int, если нельзя, к float, 
        # если нельзя, к bool, если нельзя, оставим str
        # bool здесь tricky, предполагаем, что bool - это True/False/1/0/yes/no?
        # Или оставим логику проще: если все значения либо "True"/"False"/"0"/"1" - bool
        new_types = {}
        for col_name in self.columns:
            col_index = self.columns.index(col_name)
            col_values = [str(row[col_index]) for row in self.data]

            # Порядок проверки: int -> float -> bool -> str
            def can_convert_to_int(vals):
                try:
                    for v in vals:
                        int(v)
                    return True
                except:
                    return False

            def can_convert_to_float(vals):
                try:
                    for v in vals:
                        float(v)
                    return True
                except:
                    return False

            def can_convert_to_bool(vals):
                for v in vals:
                    lv = v.lower()
                    if lv not in ["true", "false", "0", "1", "yes", "no"]:
                        return False
                return True

            if can_convert_to_int(col_values):
                new_types[col_name] = int
            elif can_convert_to_float(col_values):
                new_types[col_name] = float
            elif can_convert_to_bool(col_values):
                new_types[col_name] = bool
            else:
                new_types[col_name] = str

        # Применим новые типы
        for col_name, t in new_types.items():
            self._convert_column(col_name, t)

    @staticmethod
    def concat(table1, table2):
        # Склеивает две таблицы по вертикали, при совпадении столбцов
        if table1.columns != table2.columns:
            raise StructureMismatchError("Структура столбцов не совпадает")
        # Предполагается, что и типы совпадают, иначе нужно приводить или кидать исключение
        # Проверим типы
        for col in table1.columns:
            if table1.types[col] != table2.types[col]:
                raise StructureMismatchError("Типы столбцов не совпадают")

        new_data = table1.data + table2.data
        # Не копируем сверх меры, предположим, что concat создает новую таблицу
        return Table(columns=table1.columns[:], data=deepcopy(new_data), types=deepcopy(table1.types))

    def split(self, row_number):
        # Разбивает таблицу на две по номеру строки
        if not (0 <= row_number <= len(self.data)):
            raise InvalidRowError("Индекс строки вне диапазона")
        data1 = self.data[:row_number]
        data2 = self.data[row_number:]
        t1 = Table(columns=self.columns[:], data=deepcopy(data1), types=deepcopy(self.types))
        t2 = Table(columns=self.columns[:], data=deepcopy(data2), types=deepcopy(self.types))
        return t1, t2

    # Сравнительные операции:
    # eq, gr, ls, ge, le, ne
    # Возвращают список булевых значений по указанному столбцу

    def eq(self, other, column=0):
        return self._compare(other, column, lambda x, y: x == y)

    def gr(self, other, column=0):
        return self._compare(other, column, lambda x, y: x > y)

    def ls(self, other, column=0):
        return self._compare(other, column, lambda x, y: x < y)

    def ge(self, other, column=0):
        return self._compare(other, column, lambda x, y: x >= y)

    def le(self, other, column=0):
        return self._compare(other, column, lambda x, y: x <= y)

    def ne(self, other, column=0):
        return self._compare(other, column, lambda x, y: x != y)

    def _compare(self, other, column, op):
        # other - либо значение, либо список значений
        # если значение - сравниваем все строки со значением
        # если список - длина списка должна совпадать с числом строк
        vals = self.get_values(column)
        if isinstance(other, list):
            if len(other) != len(vals):
                raise TableException("Длина списка для сравнения не совпадает с количеством строк")
            return [op(v, o) for v, o in zip(vals, other)]
        else:
            return [op(v, other) for v in vals]

    def filter_rows(self, bool_list, copy_table=False):
        # Фильтрация строк по булевому списку
        if len(bool_list) != len(self.data):
            raise BoolListLengthError("Длина булевского списка не совпадает с количеством строк")
        filtered = [row for row, flag in zip(self.data, bool_list) if flag]
        if copy_table:
            return Table(columns=deepcopy(self.columns), data=deepcopy(filtered), types=deepcopy(self.types))
        else:
            return Table(columns=self.columns, data=filtered, types=self.types)

    @staticmethod
    def merge_tables(table1, table2, by_number=True):
        # Слияние двух таблиц по строчному индексу или по номеру строки
        # Предполагается, что строки соответствуют друг другу либо по индексу (by_number=True),
        # либо по значению первого столбца (by_number=False).
        # Результат: объединенный набор столбцов. Конфликты по типам столбцов, отсутствию столбцов, несовпадению количества строк.
        # Допустим, если by_number=True, то берем i-ую строку таблицы1 и i-ую строку таблицы2 и объединяем.
        # Если длины различаются или индексы не совпадают - кидаем исключение MergeConflictError.
        # Если by_number=False - сопоставляем строки по значению первого столбца, объединяем те, что совпадают.

        if by_number:
            if len(table1.data) != len(table2.data):
                raise MergeConflictError("Число строк в таблицах не совпадает")
            # Объединяем колонки
            merged_columns = list(table1.columns)
            for c in table2.columns:
                if c not in merged_columns:
                    merged_columns.append(c)

            # Определяем типы для merged_columns
            merged_types = {}
            for c in merged_columns:
                if c in table1.types and c in table2.types:
                    if table1.types[c] != table2.types[c]:
                        raise MergeConflictError(f"Различающиеся типы столбца {c}")
                    merged_types[c] = table1.types[c]
                elif c in table1.types:
                    merged_types[c] = table1.types[c]
                else:
                    merged_types[c] = table2.types[c]

            # Строим данные
            merged_data = []
            for i in range(len(table1.data)):
                row_dict = {col: val for col, val in zip(table1.columns, table1.data[i])}
                row_dict2 = {col: val for col, val in zip(table2.columns, table2.data[i])}
                for c in table2.columns:
                    if c not in row_dict:
                        row_dict[c] = row_dict2[c]
                    else:
                        # Конфликт? Если значения разные - это конфликт
                        if row_dict[c] != row_dict2[c]:
                            raise MergeConflictError(f"Конфликт значений в столбце {c}")
                # Превратим row_dict в список по merged_columns
                merged_row = [row_dict[c] for c in merged_columns]
                merged_data.append(merged_row)

            return Table(columns=merged_columns, data=merged_data, types=merged_types)

        else:
            # Сопоставление по значению первого столбца
            if len(table1.columns) == 0 or len(table2.columns) == 0:
                raise MergeConflictError("Одна из таблиц не имеет столбцов для сопоставления")

            idx_col_1 = table1.columns[0]
            idx_col_2 = table2.columns[0]

            # Словарь table2 по индексному столбцу
            map2 = {}
            for r in table2.data:
                key = r[0]
                if key in map2:
                    raise MergeConflictError("Дублирующийся индекс в table2")
                map2[key] = r

            merged_columns = list(table1.columns)
            for c in table2.columns:
                if c not in merged_columns:
                    merged_columns.append(c)

            merged_types = {}
            for c in merged_columns:
                if c in table1.types and c in table2.types:
                    if table1.types[c] != table2.types[c]:
                        raise MergeConflictError(f"Различающиеся типы столбца {c}")
                    merged_types[c] = table1.types[c]
                elif c in table1.types:
                    merged_types[c] = table1.types[c]
                else:
                    merged_types[c] = table2.types[c]

            merged_data = []
            for row in table1.data:
                key = row[0]
                if key not in map2:
                    raise MergeConflictError(f"Строка с индексом {key} не найдена во второй таблице")
                row_dict = {col: val for col, val in zip(table1.columns, row)}
                row_dict2 = {col: val for col, val in zip(table2.columns, map2[key])}
                for c in table2.columns:
                    if c not in row_dict:
                        row_dict[c] = row_dict2[c]
                    else:
                        if row_dict[c] != row_dict2[c]:
                            raise MergeConflictError(f"Конфликт значений в столбце {c}")
                merged_row = [row_dict[c] for c in merged_columns]
                merged_data.append(merged_row)

            return Table(columns=merged_columns, data=merged_data, types=merged_types)
