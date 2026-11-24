# -*- coding: utf-8 -*-
"""生成物品借还登记表（借出 / 借入 双向记录）。"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.properties import PageSetupProperties
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter

OUT = r"E:\git\Note\物品借还登记表.xlsx"
ROWS = 200  # 数据行数：第 2 行 ~ 第 201 行

FONT = "微软雅黑"
HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
BAND_FILL = PatternFill("solid", fgColor="F5F8FC")
THIN = Side(style="thin", color="D0D7E2")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

wb = Workbook()

# ---------------------------------------------------------------- 借还记录
ws = wb.active
ws.title = "借还记录"
ws.sheet_properties.tabColor = "1F4E79"

headers = [
    ("序号", 6),
    ("类型", 9),
    ("物品名称", 22),
    ("规格/型号", 18),
    ("数量", 7),
    ("借用人/出借人", 15),
    ("联系方式", 15),
    ("借出日期", 13),
    ("约定归还日期", 14),
    ("实际归还日期", 14),
    ("状态", 10),
    ("备注", 28),
]

for col, (title, width) in enumerate(headers, start=1):
    cell = ws.cell(row=1, column=col, value=title)
    cell.font = Font(name=FONT, size=11, bold=True, color="FFFFFF")
    cell.fill = HEADER_FILL
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = BORDER
    ws.column_dimensions[get_column_letter(col)].width = width
ws.row_dimensions[1].height = 32

last = ROWS + 1
for r in range(2, last + 1):
    ws.row_dimensions[r].height = 22
    for c in range(1, 13):
        cell = ws.cell(row=r, column=c)
        cell.font = Font(name=FONT, size=10, color="404040")
        cell.border = BORDER
        cell.alignment = Alignment(
            horizontal="center" if c in (1, 2, 5, 8, 9, 10, 11) else "left",
            vertical="center",
        )
        if r % 2 == 0:
            cell.fill = BAND_FILL
    # 序号：有物品名称才显示
    ws.cell(row=r, column=1, value=f'=IF($C{r}="","",ROW()-1)').font = Font(
        name=FONT, size=10, color="808080"
    )
    # 状态：实际归还 > 逾期 > 未归还
    ws.cell(
        row=r,
        column=11,
        value=(
            f'=IF($C{r}="","",IF($J{r}<>"","已归还",'
            f'IF(AND($I{r}<>"",$I{r}<TODAY()),"已逾期","未归还")))'
        ),
    )
    for c in (8, 9, 10):
        ws.cell(row=r, column=c).number_format = "yyyy-mm-dd"
    ws.cell(row=r, column=5).number_format = "0"

# 下拉选项：类型
dv_type = DataValidation(
    type="list", formula1='"借出,借入"', allow_blank=True, showDropDown=False
)
dv_type.showErrorMessage = True
dv_type.showInputMessage = True
dv_type.promptTitle = "类型"
dv_type.prompt = "借出：我把物品借给别人；借入：我向别人借物品"
dv_type.error = "请从下拉列表中选择：借出 或 借入"
dv_type.errorTitle = "输入无效"
ws.add_data_validation(dv_type)
dv_type.add(f"B2:B{last}")

# 数量
dv_qty = DataValidation(
    type="whole", operator="between", formula1="1", formula2="9999", allow_blank=True
)
dv_qty.showErrorMessage = True
dv_qty.errorTitle = "数量无效"
dv_qty.error = "数量应为 1~9999 的整数"
ws.add_data_validation(dv_qty)
dv_qty.add(f"E2:E{last}")

# 日期
dv_date = DataValidation(
    type="date",
    operator="between",
    formula1="DATE(2000,1,1)",
    formula2="DATE(2100,12,31)",
    allow_blank=True,
)
dv_date.showErrorMessage = True
dv_date.errorTitle = "日期无效"
dv_date.error = "请输入日期，例如 2026-11-24"
ws.add_data_validation(dv_date)
dv_date.add(f"H2:J{last}")

# 状态自动着色
rng = f"K2:K{last}"
ws.conditional_formatting.add(
    rng,
    FormulaRule(
        formula=['$K2="已逾期"'],
        fill=PatternFill("solid", fgColor="FFC7CE"),
        font=Font(name=FONT, size=10, bold=True, color="9C0006"),
    ),
)
ws.conditional_formatting.add(
    rng,
    FormulaRule(
        formula=['$K2="未归还"'],
        fill=PatternFill("solid", fgColor="FFEB9C"),
        font=Font(name=FONT, size=10, color="9C5700"),
    ),
)
ws.conditional_formatting.add(
    rng,
    FormulaRule(
        formula=['$K2="已归还"'],
        fill=PatternFill("solid", fgColor="C6EFCE"),
        font=Font(name=FONT, size=10, color="006100"),
    ),
)

ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:L{last}"
ws.sheet_view.zoomScale = 100

# 打印设置：横向、表头重复、按宽度缩放
ws.page_setup.orientation = "landscape"
ws.page_setup.paperSize = ws.PAPERSIZE_A4
ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
ws.print_title_rows = "1:1"
ws.print_options.horizontalCentered = True

# ---------------------------------------------------------------- 统计
st = wb.create_sheet("统计")
st.sheet_properties.tabColor = "2E75B6"
st.sheet_view.showGridLines = False
st.column_dimensions["A"].width = 22
st.column_dimensions["B"].width = 12
st.column_dimensions["C"].width = 4
st.column_dimensions["D"].width = 46

st.merge_cells("A1:D1")
t = st["A1"]
t.value = "物品借还统计"
t.font = Font(name=FONT, size=16, bold=True, color="1F4E79")
t.alignment = Alignment(horizontal="left", vertical="center")
st.row_dimensions[1].height = 34

st.merge_cells("A2:D2")
s = st["A2"]
s.value = "下列数字随「借还记录」自动更新，无需手工填写"
s.font = Font(name=FONT, size=9, color="808080")

stat_rows = [
    ("记录总数", f'=COUNTA(借还记录!$C$2:$C${last})'),
    ("未归还", f'=COUNTIF(借还记录!$K$2:$K${last},"未归还")'),
    ("已逾期", f'=COUNTIF(借还记录!$K$2:$K${last},"已逾期")'),
    ("已归还", f'=COUNTIF(借还记录!$K$2:$K${last},"已归还")'),
    ("未归还合计", "=B5+B6"),
    ("其中：我借出未还", f'=COUNTIFS(借还记录!$B$2:$B${last},"借出",借还记录!$K$2:$K${last},"未归还")'
                       f'+COUNTIFS(借还记录!$B$2:$B${last},"借出",借还记录!$K$2:$K${last},"已逾期")'),
    ("其中：我借入未还", f'=COUNTIFS(借还记录!$B$2:$B${last},"借入",借还记录!$K$2:$K${last},"未归还")'
                       f'+COUNTIFS(借还记录!$B$2:$B${last},"借入",借还记录!$K$2:$K${last},"已逾期")'),
]

start = 4
for i, (label, formula) in enumerate(stat_rows):
    r = start + i
    lc = st.cell(row=r, column=1, value=label)
    lc.font = Font(name=FONT, size=11, bold=i >= 4, color="404040")
    lc.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    lc.border = BORDER
    vc = st.cell(row=r, column=2, value=formula)
    vc.font = Font(name=FONT, size=13, bold=True, color="1F4E79")
    vc.alignment = Alignment(horizontal="center", vertical="center")
    vc.number_format = "0"
    vc.border = BORDER
    st.row_dimensions[r].height = 26

# 说明
st["A13"] = "说明"
st["A13"].font = Font(name=FONT, size=10, bold=True, color="1F4E79")
st.merge_cells("A14:D14")
n = st["A14"]
n.value = "「未归还合计」= 未归还 + 已逾期；逾期判定依据“约定归还日期”与当天日期。"
n.font = Font(name=FONT, size=9, color="808080")
n.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
st.row_dimensions[14].height = 30

# ---------------------------------------------------------------- 使用说明
doc = wb.create_sheet("使用说明")
doc.sheet_properties.tabColor = "A6A6A6"
doc.sheet_view.showGridLines = False
doc.column_dimensions["A"].width = 112

lines = [
    ("物品借还登记表 · 使用说明", "title"),
    ("", ""),
    ("一、用途", "h"),
    ("把物品借给别人（借出）和向别人借物品（借入）都记在同一张表里，靠“类型”列区分，方便日后核对与催还。", "p"),
    ("", ""),
    ("二、各列怎么填", "h"),
    ("类型：下拉选择「借出」或「借入」。借出 = 我的物品借给别人；借入 = 我借了别人的物品。", "p"),
    ("物品名称、规格/型号：写清具体物品，避免同名混淆，例如“万用表 / 优利德 UT61E”。", "p"),
    ("数量：借出或借入的件数，填写整数。", "p"),
    ("借用人/出借人：借出时填借走的人，借入时填物品的主人；联系方式填电话或微信，方便催还。", "p"),
    ("借出日期：实际交付物品的日期；约定归还日期：双方约定的归还时间，可不填。", "p"),
    ("实际归还日期：物品回到手上的当天填写，留空表示尚未归还。", "p"),
    ("状态：公式自动生成，不用手填——填了实际归还日期即“已归还”；超过约定日期未还显示“已逾期”并标红；其余为“未归还”。", "p"),
    ("备注：用途、损耗、配件数量等补充信息。", "p"),
    ("", ""),
    ("三、使用建议", "h"),
    ("1. 表头已开启筛选，可按类型、状态、对方姓名快速查找；第 1 行已冻结，向下滚动时表头始终可见。", "p"),
    ("2. 预留 200 行（第 2~201 行），不够用时在表格中间插入整行，公式与格式会自动延续。", "p"),
    ("3. 日期统一按 年-月-日 录入，例如 2026-11-24；直接输入即可被识别为日期。", "p"),
    ("4. “统计”页自动汇总记录总数、未归还、已逾期、已归还等数量。", "p"),
    ("5. 如果只关心当前未归还的物品，在“状态”列筛选“未归还”和“已逾期”即可。", "p"),
    ("", ""),
    ("四、填写示例（仅示意，未写入表中）", "h"),
    ("借出 | 万用表 | 优利德 UT61E | 1 | 张三 | 138****0000 | 2026-11-24 | 2026-12-01 | （空） | 自动显示“未归还” | 出差借用", "eg"),
]

r = 1


def est_height(text, units=112.0, per_line=16.0):
    visual = sum(2 if ord(ch) > 127 else 1 for ch in text)
    lines_count = max(1, int(-(-visual // (units * 0.95))))
    return lines_count * per_line + 8


for text, kind in lines:
    c = doc.cell(row=r, column=1, value=text)
    if kind == "title":
        c.font = Font(name=FONT, size=18, bold=True, color="1F4E79")
        doc.row_dimensions[r].height = 40
        c.alignment = Alignment(vertical="center")
    elif kind == "h":
        c.font = Font(name=FONT, size=12, bold=True, color="2E75B6")
        doc.row_dimensions[r].height = 28
        c.alignment = Alignment(vertical="center")
    elif kind == "eg":
        c.font = Font(name="Consolas", size=10, color="404040")
        c.fill = PatternFill("solid", fgColor="F2F2F2")
        c.alignment = Alignment(vertical="center", wrap_text=True)
        doc.row_dimensions[r].height = est_height(text, 118, 16) + 6
    elif kind == "p":
        c.font = Font(name=FONT, size=10, color="404040")
        c.alignment = Alignment(vertical="top", wrap_text=True)
        doc.row_dimensions[r].height = est_height(text)
    r += 1

doc.sheet_view.zoomScale = 100
wb.active = 0
wb.properties.title = "物品借还登记表"
wb.properties.subject = "借用 / 借出物品登记与归还跟踪"
wb.properties.creator = ""
wb.calculation.fullCalcOnLoad = True
wb.save(OUT)
print("saved:", OUT)
