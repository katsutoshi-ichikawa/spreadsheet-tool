import gspread
from google.oauth2.service_account import Credentials

# 認証に必要な権限の設定
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# JSONファイルを使って認証
creds = Credentials.from_service_account_file(
    "spreadsheet-tool-495211-6a9810c661f6.json",
    scopes=SCOPES,
)

# Googleスプレッドシートに接続
client = gspread.authorize(creds)

print("接続成功！")

# ここにスプレッドシートのURLを貼り付けてください
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1kEyfjH_aKlPOIKIbjYDN7kYoBglcI-hzPeSZoItpEKY/edit?gid=0#gid=0"

sheet = client.open_by_url(SPREADSHEET_URL)
print(f"スプレッドシート名: {sheet.title}")
