class TableException(Exception):
    """Базовое исключение для операций с таблицами."""
    pass

class StructureMismatchError(TableException):
    """Исключение, вызываемое, когда структуры таблиц не совпадают."""
    pass

class InvalidColumnError(TableException):
    """Исключение, вызываемое при неверной работе со столбцом."""
    pass

class InvalidRowError(TableException):
    """Исключение, вызываемое при неверной работе со строками."""
    pass

class TypeConversionError(TableException):
    """Исключение, вызываемое при ошибке преобразования типа."""
    pass

class MergeConflictError(TableException):
    """Исключение при конфликтном слиянии таблиц."""
    pass

class BoolListLengthError(TableException):
    """Исключение, если булевский список фильтрации не совпадает с количеством строк."""
    pass
