import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_file(
    "spreadsheet-tool-495211-6a9810c661f6.json",
    scopes=SCOPES,
)

client = gspread.authorize(creds)
spreadsheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1kEyfjH_aKlPOIKIbjYDN7kYoBglcI-hzPeSZoItpEKY/edit?gid=0#gid=0"
)

# シート一覧を表示
print("=== シート一覧 ===")
for i, ws in enumerate(spreadsheet.worksheets()):
    print(f"{i}: {ws.title}")

# 最初のシートの内容を確認
print("\n=== 最初のシートの内容（先頭10行）===")
first_sheet = spreadsheet.worksheets()[0]
rows = first_sheet.get_all_values()
for row in rows[:10]:
    print(row)
