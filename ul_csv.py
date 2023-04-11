import gspread, csv, glob
from oauth2client.service_account import ServiceAccountCredentials


year = 2023
month = 3
glob_csv = glob.glob("*.csv")
if glob_csv == []:
    print(">>>> No Such csv file!!")
    exit()
csv_file_name = glob_csv[0]


# クレデンシャル情報の設定
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("./credentials.json", scope)
gc = gspread.authorize(credentials)


spreadsheet_name = f"家計簿_{year}"
spreadsheet = gc.open(spreadsheet_name)
worksheet = spreadsheet.worksheet(f"{month}月")

spreadsheet.values_clear(f"{month}月!Q1:Z200")
csv_list = list(csv.reader(open(csv_file_name, encoding="shift_jis")))
# csv.readerで読み込んだものは全て文字列となるため、金額部分のみint型に変更
for row in csv_list[1:]:
    row[3] = int(row[3])
worksheet.update("Q1:Z200", csv_list)