import openpyxl
from pathlib import Path

def read_column(file_path, sheet_name='Sheet1', col=1, header=False):
    """Read a column from Excel and return list of values.
    file_path can be Path or str.
    If header=True, skip the first row."""
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb[sheet_name]
    start = 2 if header else 1
    vals = []
    for row in sheet.iter_rows(min_row=start, values_only=True):
        v = row[col-1]
        if v is None:
            continue
        vals.append(str(v).strip())
    return vals