# -*- coding: utf-8 -*-
"""校验生成的登记表：结构、公式、缓存值、校验规则、条件格式。"""
from openpyxl import load_workbook

P = r"E:\git\Note\物品借还登记表.xlsx"
wb = load_workbook(P, data_only=False)
wbv = load_workbook(P, data_only=True)

print("sheets:", wb.sheetnames)
ws = wb["借还记录"]
print("dims:", ws.dimensions, "freeze:", ws.freeze_panes, "filter:", ws.auto_filter.ref)
print("headers:", [ws.cell(row=1, column=c).value for c in range(1, 13)])
print("C2:", repr(ws["C2"].value), "K2 formula:", ws["K2"].value)
print("K201 formula:", ws["K201"].value[:60], "...")
print("validations:", len(ws.data_validations.dataValidation))
for dv in ws.data_validations.dataValidation:
    print("  dv:", dv.type, dv.sqref, dv.formula1, "|", dv.formula2)
print("CF ranges:", list(ws.conditional_formatting))
for cf in ws.conditional_formatting:
    for rule in cf.rules:
        print("  rule:", cf.sqref, rule.type, rule.formula, rule.dxf.fill.fgColor.rgb if rule.dxf and rule.dxf.fill else None)
print("widths:", {k: round(v.width, 1) for k, v in list(ws.column_dimensions.items())[:12]})
print("print:", ws.page_setup.orientation, ws.print_title_rows, ws.page_setup.fitToWidth)
print("header fill:", ws["A1"].fill.fgColor.rgb, "font:", ws["A1"].font.name, ws["A1"].font.bold)
print("numfmt H2/J2:", ws["H2"].number_format, ws["J2"].number_format)

st = wb["统计"]
stv = wbv["统计"]
for r in range(4, 11):
    print("stat", r, st.cell(row=r, column=1).value, "|", st.cell(row=r, column=2).value,
          "=> cached:", stv.cell(row=r, column=2).value)

doc = wb["使用说明"]
print("doc rows:", doc.max_row, "| A1:", doc["A1"].value)
for r in range(1, doc.max_row + 1):
    v = doc.cell(row=r, column=1).value
    if v:
        print(" ", r, v[:40])

print("tab colors:", [s.sheet_properties.tabColor.rgb if s.sheet_properties.tabColor else None for s in wb.worksheets])
