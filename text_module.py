def save_table(table, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        # Аналог print_table
        f.write(" | ".join(table.columns) + "\n")
        f.write("-" * (3 * len(table.columns)) + "\n")
        for row in table.data:
            f.write(" | ".join(str(x) for x in row) + "\n")
