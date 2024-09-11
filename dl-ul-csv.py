import csv
import glob
import os
import re
import subprocess

# from webdriver_manager.chrome import ChromeDriverManager
from time import sleep, strftime

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

import settings

#### 家計簿csvのダウンロード ####
# 家計簿の年月を指定
year, month = map(int, input().split())
EMAIL = settings.MFEMAIL
PASSWORD = settings.MFPASSWORD
TWO_STEP_AUTHENTICATION_CODE = settings.TWO_STEP_AUTHENTICATION_CODE
options = ChromeOptions()
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36')
options.add_experimental_option("prefs",{"download.prompt_for_download":False})
service = ChromeService("/usr/bin/chromedriver") # ChromeDriverManager().install()を使いたい
browser = webdriver.Chrome(service=service, options=options)
browser.command_executor._commands["send_command"] = (
    'POST',
    '/session/$sessionId/chromium/send_command'
)
browser.execute(
    "send_command",
    params={
        'cmd': 'Page.setDownloadBehavior',
        'params': { 'behavior': 'allow',"downloadPath":"/workspace"}
    }
)
browser.get("https://moneyforward.com/login")

elem_login = browser.find_element(By.XPATH, "//*[@id=\"login\"]/div/div/div[3]/a")
elem_login.click()
sleep(3)

# メールアドレスを入力＆ログイン
print(">>>> start input mail...")
elem_input_email = browser.find_element(By.XPATH, "//*[@id=\"mfid_user[email]\"]")
elem_input_email.send_keys(EMAIL)

elem_login = browser.find_element(By.XPATH, "//*[@id=\"submitto\"]")
elem_login.click()
print(">>>> done!")
sleep(3)

# パスワード入力＆ログイン
print(">>>> start input password...")
elem_input_password = browser.find_element(By.XPATH, "//*[@id=\"mfid_user[password]\"]")
elem_input_password.send_keys(PASSWORD)

elem_login2 = browser.find_element(By.XPATH, "//*[@id=\"submitto\"]")
elem_login2.click()
print(">>>> done!")
sleep(3)

# 二段階認証
print(">>>> start input two step authentication code...")
two_step_authentication = ["oathtool", "--totp", "--base32", TWO_STEP_AUTHENTICATION_CODE]
auth_code = re.findall(r'\d+', subprocess.check_output(two_step_authentication).decode("utf-8"))

elem_input_authcode = browser.find_element(By.XPATH, "//*[@id=\"otp_attempt\"]")
elem_input_authcode.send_keys(auth_code[0])
elem_login3 = browser.find_element(By.XPATH, "//*[@id=\"submitto\"]")
elem_login3.click()
print(">>>> done!")
sleep(3)

# 家計簿ページへ
print(">>>> enter the main page...")
elem_kakeibo = browser.find_element(By.XPATH, "//*[@id=\"header-container\"]/header/div[2]/ul/li[2]/a")
elem_kakeibo.click()
sleep(3)

# 家計簿をダウンロードするために年月を指定する
print(">>>> enter the kakeibo page & select year and month...")
elem_select_year_and_month = browser.find_element(By.XPATH, "//*[@id=\"in_out\"]/div[2]/div/span")
elem_select_year_and_month.click()

actions = ActionChains(browser)
actions.move_to_element(browser.find_element(By.XPATH, f"//*[@id=\"in_out\"]/div[2]/div/div/div[{int(strftime('%Y'))-year+1}]"))
actions.move_to_element(browser.find_element(By.XPATH, f"//*[@id=\"in_out\"]/div[2]/div/div/div[{int(strftime('%Y'))-year+1}]/div/a[{month}]"))
actions.click()
actions.perform()
sleep(3)


# csvをダウンロード
print(">>>> downloading...")
elem_download_dropdown = browser.find_element(By.XPATH, "//*[@id=\"js-dl-area\"]/a")
elem_download_dropdown.click()
sleep(3)
elem_dlcsv = browser.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div/section/section/div[4]/span/div/ul/li[1]/table/tbody/tr/td[2]/span/a")
elem_dlcsv.click() 
print(">>>> every program completed")
browser.close()


#### スプレッドシートにcsvをアップロード ####

scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("./credentials.json", scope)
gc = gspread.authorize(credentials)

# csvファイルが同階層にない場合プログラムを終了
glob_csv = glob.glob("*.csv")
if glob_csv == []:
    print(">>>> No Such csv File!! Please Download csv File.")
    exit()
    
csv_file_name = glob_csv[0]
spreadsheet_name = f"家計簿_{year}"
spreadsheet = gc.open(spreadsheet_name)
worksheet = spreadsheet.worksheet(f"{month}月")

spreadsheet.values_clear(f"{month}月!Q1:Z200")
csv_list = list(csv.reader(open(csv_file_name, encoding="shift_jis")))

# csv.readerで読み込んだものは全て文字列となるため、金額部分のみint型に変更
for row in csv_list[1:]:
    row[3] = int(row[3])
    
worksheet.update("Q1:Z200", csv_list)
os.remove(f"{csv_file_name}")
