# スプレッドシート集計ツール
import os
import re
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1kEyfjH_aKlPOIKIbjYDN7kYoBglcI-hzPeSZoItpEKY/edit"
JSON_FILE = os.environ.get("SA_KEY_PATH", "/home/ichikawa/spreadsheet-tool-495211-6a9810c661f6.json")

# サマリーに含める主要科目（順番どおりに出力）
TARGET_SUBJECTS = [
    "純売上高",
    "売上総利益",
    "営業利益",
    "人件費",
    "販売費及び一般管理費計",
]

# 有効な月名
VALID_MONTHS = {"4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月", "1月", "2月", "3月"}


def parse_number(value):
    """' 1,234,567 ' や '(1,234)' のような文字列を数値に変換する"""
    value = value.strip().replace(" ", "").replace(",", "")
    if value == "":
        return None
    if value.startswith("(") and value.endswith(")"):
        value = "-" + value[1:-1]
    try:
        return float(value)
    except ValueError:
        return None


def get_two_period_totals(worksheet, subject):
    """
    1つのシートから指定科目の2期分データを取得する。
    シートは [前期データ][当期データ] の順で格納されている前提。
    - group1_total: 前期合計（グループ1）
    - group2_total: 当期合計（グループ2）
    """
    rows = worksheet.get_all_values()
    groups = []
    current_group_total = 0.0
    current_group_months = set()
    current_group_count = 0

    for row in rows:
        if len(row) < 3:
            continue
        month = row[0].strip()
        subject_cell = row[1].strip()
        value_str = row[2].strip()

        if subject_cell != subject:
            continue
        if month not in VALID_MONTHS:
            continue

        if month in current_group_months:
            # 同じ月が再登場 → 新しいグループへ
            groups.append((current_group_total, current_group_count))
            current_group_total = 0.0
            current_group_months = set()
            current_group_count = 0

        value = parse_number(value_str)
        if value is not None:
            current_group_total += value
            current_group_months.add(month)
            current_group_count += 1

    # 最後のグループを追加
    if current_group_count > 0:
        groups.append((current_group_total, current_group_count))

    if len(groups) >= 2:
        prev_total, prev_months = groups[0]
        current_total, current_months = groups[1]
    elif len(groups) == 1:
        prev_total, prev_months = 0.0, 0
        current_total, current_months = groups[0]
    else:
        prev_total, prev_months = 0.0, 0
        current_total, current_months = 0.0, 0

    return int(current_total), current_months, int(prev_total), prev_months


def get_period_sheets(spreadsheet):
    """「XX期損益」シートを期番号の降順で返す"""
    period_sheets = []
    for ws in spreadsheet.worksheets():
        match = re.match(r"(\d+)期損益", ws.title)
        if match:
            period_num = int(match.group(1))
            period_sheets.append((period_num, ws))
    period_sheets.sort(key=lambda x: x[0], reverse=True)
    return period_sheets


def main():
    creds = Credentials.from_service_account_file(JSON_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_url(SPREADSHEET_URL)

    period_sheets = get_period_sheets(spreadsheet)
    if len(period_sheets) < 1:
        print("損益シートが見つかりません")
        return

    # 最新期のシートから当期・前期の両方を取得
    current_num, current_ws = period_sheets[0]
    prev_num = current_num - 1

    print(f"集計シート: {current_ws.title}")
    print(f"当期: {current_num}期  前期: {prev_num}期")
    print()

    header = [
        "科目名",
        f"{current_num}期 合計",
        f"{prev_num}期 合計",
        "増減",
        "増減率(%)",
    ]
    rows_out = [header]

    for subject in TARGET_SUBJECTS:
        cur_total, cur_months, prev_total, prev_months = get_two_period_totals(current_ws, subject)

        if prev_total != 0:
            diff = cur_total - prev_total
            rate = round(diff / abs(prev_total) * 100, 1)
        else:
            diff = cur_total
            rate = ""

        rows_out.append([subject, cur_total, prev_total, diff, rate])

        sign = "+" if diff >= 0 else ""
        print(f"{subject}")
        print(f"  {current_num}期: {cur_total:>15,}円  ({cur_months}ヶ月)")
        print(f"  {prev_num}期: {prev_total:>15,}円  ({prev_months}ヶ月)")
        print(f"  増減: {sign}{diff:,}円  ({sign}{rate}%)")
        print()

    # サマリーシートを作成（既存は削除して再作成）
    summary_title = f"{current_num}期vs{prev_num}期サマリー"
    try:
        spreadsheet.del_worksheet(spreadsheet.worksheet(summary_title))
    except gspread.exceptions.WorksheetNotFound:
        pass

    summary_ws = spreadsheet.add_worksheet(title=summary_title, rows=len(rows_out) + 5, cols=6)
    summary_ws.update(rows_out, "A1")

    print(f"サマリーシート「{summary_title}」を作成しました")


if __name__ == "__main__":
    main()
