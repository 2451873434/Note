# -*- coding: utf-8 -*-
"""校验交付文件 + 生成公式自测副本。"""
import datetime as dt
from openpyxl import load_workbook

P = r"E:\git\Note\物品借还登记表.xlsx"
wb = load_workbook(P)
ws = wb["借还记录"]
print("sheets:", wb.sheetnames)
print("dim:", ws.dimensions, "| freeze:", ws.freeze_panes, "| filter:", ws.auto_filter.ref)
print("headers:")
for c in range(1, 13):
    print("   ", c, ws.cell(row=1, column=c).value, "| w=", ws.column_dimensions[chr(64 + c)].width)
print("K2:", ws["K2"].value)
print("A2:", ws["A2"].value)
print("DV count:", len(ws.data_validations.dataValidation))
for dv in ws.data_validations.dataValidation:
    print("  ", dv.type, dv.sqref, "showErr=", dv.showErrorMessage, "showPrompt=", dv.showInputMessage,
          "|", dv.formula1, dv.formula2, "|", dv.promptTitle)
print("CF:", [(str(cf.sqref), [(r.formula, r.dxf.fill.fgColor.rgb, r.dxf.fill.bgColor.rgb) for r in cf.rules])
              for cf in ws.conditional_formatting])
print("stat formulas:")
st = wb["统计"]
for r in range(4, 11):
    print("  ", st.cell(row=r, column=1).value, "->", st.cell(row=r, column=2).value)
print("fullCalcOnLoad:", wb.calculation.fullCalcOnLoad)

# ---- 公式自测副本 ----
t = load_workbook(P)
tw = t["借还记录"]
samples = [
    ("借出", "万用表", "UT61E", 1, "张三", "13800000000", dt.date(2026, 11, 20), dt.date(2026, 12, 1), None, "出差借用"),
    ("借出", "电动螺丝刀", "博世 GO2", 1, "李四", "微信 lisi", dt.date(2026, 10, 8), dt.date(2026, 11, 1), None, "长期未还"),
    ("借入", "示波器", "泰克 TBS1102", 1, "王五", "wangwu@corp", dt.date(2026, 11, 15), dt.date(2026, 11, 30), dt.date(2026, 11, 22), "已按期归还"),
]
for i, s in enumerate(samples, start=2):
    for col, val in zip(range(2, 13), (s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], None, s[9])):
        if col == 11:
            continue
        tw.cell(row=i, column=col, value=val)
t.save(r"E:\git\Note\_test_ledger.xlsx")
print("test copy saved")
