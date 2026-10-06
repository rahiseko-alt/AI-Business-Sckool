"""別のブックのシートを、値・式・書式・結合・列幅ごと写す（openpyxl はブック間のシート複製を持たないため）。"""

from copy import copy


def copy_sheet(src, dst_wb, title: str):
    ws = dst_wb.create_sheet(title)
    for row in src.iter_rows():
        for cell in row:
            if type(cell).__name__ == "MergedCell":
                continue
            out = ws.cell(cell.row, cell.column, cell.value)
            if cell.has_style:
                out.font, out.fill, out.border = copy(cell.font), copy(cell.fill), copy(cell.border)
                out.alignment, out.protection = copy(cell.alignment), copy(cell.protection)
                out.number_format = cell.number_format
    for rng in src.merged_cells.ranges:
        ws.merge_cells(str(rng))
    for key, dim in src.column_dimensions.items():
        ws.column_dimensions[key].width = dim.width
        ws.column_dimensions[key].hidden = dim.hidden
    for key, dim in src.row_dimensions.items():
        ws.row_dimensions[key].height = dim.height
    ws.freeze_panes = src.freeze_panes
    ws.sheet_format = copy(src.sheet_format)
    ws.page_setup.orientation = src.page_setup.orientation
    return ws
