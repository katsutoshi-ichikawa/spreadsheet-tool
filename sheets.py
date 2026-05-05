import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
from collections import defaultdict

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1kEyfjH_aKlPOIKIbjYDN7kYoBglcI-hzPeSZoItpEKY/edit"
JSON_FILE = os.environ.get("SA_KEY_PATH", "/home/ichikawa/spreadsheet-tool-495211-6a9810c661f6.json")

COL_CODE   = 0   # 個人.従業員コード
COL_LNAME  = 1   # 個人.ビジネスネーム姓
COL_FNAME  = 2   # 個人.ビジネスネーム名
COL_BIRTH  = 7   # 個人.生年月日
COL_HIRE   = 8   # 個人.入社日
COL_ROLE   = 15  # 個人.役職
COL_DEPT   = 17  # 個人.部署
COL_STATUS = 19  # 個人.就業状況


def _client():
    creds = Credentials.from_service_account_file(JSON_FILE, scopes=SCOPES)
    return gspread.authorize(creds)


def get_kot_sheets():
    """KOTXXシートの一覧を新しい順で返す"""
    client = _client()
    spreadsheet = client.open_by_url(SPREADSHEET_URL)
    sheets = [ws.title for ws in spreadsheet.worksheets() if ws.title.startswith("KOT")]
    return sorted(sheets, reverse=True)


def _classify(role):
    if role == "クルー":
        return "アルバイト"
    elif role == "":
        return "スポットワーカー"
    elif role == "その他":
        return "その他"
    return "社員"


def _calc_age(birth_str):
    if not birth_str:
        return None
    try:
        parts = birth_str.replace("-", "/").split("/")
        birth = date(int(parts[0]), int(parts[1]), int(parts[2]))
        today = date.today()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    except Exception:
        return None


def _load_active(sheet_name):
    """在職中の行だけ返す（A〜T列のみ取得）"""
    client = _client()
    spreadsheet = client.open_by_url(SPREADSHEET_URL)
    ws = spreadsheet.worksheet(sheet_name)
    rows = ws.get("A:T")
    active = []
    for r in rows[1:]:
        padded = r + [""] * (20 - len(r))
        if padded[COL_STATUS] == "在職中":
            active.append(padded)
    return active


def _get_dept_order():
    """部署マスタシートの並び順でリストを返す"""
    client = _client()
    spreadsheet = client.open_by_url(SPREADSHEET_URL)
    ws = spreadsheet.worksheet("部署マスタ")
    rows = ws.get_all_values()
    # ヘッダー行をスキップ、3列目（部署名）を順番に取得
    return [r[2] for r in rows[1:] if len(r) >= 3 and r[2]]


def get_summary(sheet_name):
    """店舗別×区分の人数サマリーを部署マスタの順で返す"""
    rows = _load_active(sheet_name)
    counts = defaultdict(lambda: {"社員": 0, "アルバイト": 0, "スポットワーカー": 0, "その他": 0})
    for r in rows:
        dept = r[COL_DEPT] or "（未設定）"
        counts[dept][_classify(r[COL_ROLE])] += 1

    dept_order = _get_dept_order()
    order_map = {dept: i for i, dept in enumerate(dept_order)}

    result = []
    for dept, c in sorted(counts.items(), key=lambda x: order_map.get(x[0], len(dept_order))):
        result.append({
            "dept": dept,
            "seiki": c["社員"],
            "part": c["アルバイト"],
            "spot": c["スポットワーカー"],
            "other": c["その他"],
            "total": sum(c.values()),
        })
    return result, len(rows)


def get_store_employees(sheet_name, store_name):
    """指定店舗の在職者一覧を返す"""
    rows = _load_active(sheet_name)
    employees = []
    for r in rows:
        dept = r[COL_DEPT] or "（未設定）"
        if dept != store_name:
            continue
        name = (r[COL_LNAME] + r[COL_FNAME]).strip()
        employees.append({
            "code": r[COL_CODE],
            "name": name,
            "role": r[COL_ROLE] or "（空欄）",
            "category": _classify(r[COL_ROLE]),
            "hire_date": r[COL_HIRE],
            "age": _calc_age(r[COL_BIRTH]),
        })
    order = {"社員": 0, "アルバイト": 1, "スポットワーカー": 2, "その他": 3}
    employees.sort(key=lambda x: (order.get(x["category"], 9), x["hire_date"]))
    return employees
