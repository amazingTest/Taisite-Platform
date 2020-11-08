from xlsxwriter.worksheet import (
    Worksheet, cell_number_tuple, cell_string_tuple)
from typing import Optional


class ExcelSheetHelperFunctions:
    def __init__(self):
        pass

    @staticmethod
    def set_column_auto_width(worksheet: Worksheet, column: int):
        """
        Set the width automatically on a column in the `Worksheet`.
        !!! Make sure you run this function AFTER having all cells filled in
        the worksheet!
        """
        max_width = ExcelSheetHelperFunctions.get_column_width(worksheet=worksheet, column=column)
        if max_width is None:
            return
        elif max_width > 45:
            max_width = 45
        worksheet.set_column(first_col=column, last_col=column, width=max_width)

    @staticmethod
    def get_column_width(worksheet: Worksheet, column: int) -> Optional[int]:
        """Get the max column width in a `Worksheet` column."""
        strings = getattr(worksheet, '_ts_all_strings', None)
        if strings is None:
            strings = worksheet._ts_all_strings = sorted(
                worksheet.str_table.string_table,
                key=worksheet.str_table.string_table.__getitem__)
        lengths = set()
        for row_id, columns_dict in worksheet.table.items():  # type: int, dict
            data = columns_dict.get(column)
            if not data:
                continue
            if type(data) is cell_string_tuple:
                iter_length = len(strings[data.string])
                if not iter_length:
                    continue
                lengths.add(iter_length)
                continue
            if type(data) is cell_number_tuple:
                iter_length = len(str(data.number))
                if not iter_length:
                    continue
                lengths.add(iter_length)
        if not lengths:
            return None
        return int(max(lengths) * 2.5)  # 中文给他加长一波
