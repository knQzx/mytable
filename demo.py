from table import Table
from csv_module import load_table as load_csv, save_table as save_csv
from pickle_module import load_table as load_pkl, save_table as save_pkl
from text_module import save_table as save_txt

# Пример создания таблицы вручную
t = Table(columns=["id", "value"], data=[[1, "100"], [2, "200"]])
t.print_table()

# Преобразование типов
t.detect_column_types()
t.print_table()

# get_values, set_values
vals = t.get_values("value")
print(vals)
t.set_values([300, 400], "value")
t.print_table()

# Сохранение/загрузка CSV
save_csv(t, "example.csv")
t2 = load_csv("example.csv", detect_types=True)
t2.print_table()

# Сохранение/загрузка Pickle
save_pkl(t2, "example.pkl")
t3 = load_pkl("example.pkl")
t3.print_table()

# Фильтрация
bool_list = t3.gr(200, "value")
filtered = t3.filter_rows(bool_list)
filtered.print_table()

# Сохранить в текстовый формат
save_txt(filtered, "example.txt")

# split
t4, t5 = t3.split(1)
t4.print_table()
t5.print_table()

# concat
t6 = Table.concat(t4, t5)
t6.print_table()

# Сравнения eq, gr, ls, ge, le, ne
print(t6.eq(300, "value"))
print(t6.gr(200, "value"))

# merge_tables
# Для демонстрации создадим вторую таблицу с такой же первой колонкой
t7 = Table(columns=["id", "extra"], data=[[1, "A"], [2, "B"]], types={"id": int, "extra": str})
merged = Table.merge_tables(t6, t7, by_number=False)
merged.print_table()
