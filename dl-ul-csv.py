from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep, strftime
from oauth2client.service_account import ServiceAccountCredentials
import subprocess, re, os, settings, glob, csv, gspread



#### 家計簿csvのダウンロード ####
# 家計簿の年月を指定
year = 2023
month = 3

EMAIL = settings.MFEMAIL
PASSWORD = settings.MFPASSWORD
TWO_STEP_AUTHENTICATION_CODE = settings.TWO_STEP_AUTHENTICATION_CODE
options = ChromeOptions()
# prefs = {
#     "profile.default_content_settings.popups": 0,
#     "download.prompt_for_download" : "false",
#     "download.directory_upgrade": "true",
#     "download.default_directory": "/home/user"
# }
# options.add_experimental_option("prefs", prefs)
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(f'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36')
service = ChromeService("/usr/bin/chromedriver") # ChromeDriverManager().install()を使いたい
browser = webdriver.Chrome(service=service, options=options)
browser.get("https://id.moneyforward.com/sign_in/email")

# メールアドレスを入力＆ログイン
print(">>>> start input mail...")
elem_input_email = browser.find_element(By.XPATH, "/html/body/main/div/div/div/div[1]/div[1]/section/form/div[2]/div/input")
elem_input_email.send_keys(EMAIL)

elem_login = browser.find_element(By.XPATH, "/html/body/main/div/div/div/div[1]/div[1]/section/form/div[2]/div/div[3]/input")
elem_login.click()
print(">>>> done!")
sleep(3)

# パスワード入力＆ログイン
print(">>>> start input password...")
elem_input_password = browser.find_element(By.XPATH, "/html/body/main/div/div/div/div/div[1]/section/form/div[2]/div/input[2]")
elem_input_password.send_keys(PASSWORD)

elem_login2 = browser.find_element(By.XPATH, "/html/body/main/div/div/div/div/div[1]/section/form/div[2]/div/div[3]/input")
elem_login2.click()
print(">>>> done!")
sleep(3)

# 二段階認証
print(">>>> start input two step authentication code...")
two_step_authentication = ["oathtool", "--totp", "--base32", TWO_STEP_AUTHENTICATION_CODE]
auth_code = re.findall(r'\d+', subprocess.check_output(two_step_authentication).decode("utf-8"))

elem_input_authcode = browser.find_element(By.XPATH, "/html/body/main/div/div/div/section/div[1]/section/form/div[2]/div/div[1]/input")
elem_input_authcode.send_keys(auth_code[0])
elem_login3 = browser.find_element(By.XPATH, "/html/body/main/div/div/div/section/div[1]/section/form/div[2]/div/div[2]/button")
elem_login3.click()
print(">>>> done!")
sleep(3)

# マネーフォワードMEのTOPページへ
print(">>>> start select service & account...")
elem_select_service_moneyforwardme = browser.find_element(By.XPATH, "/html/body/main/div/div[2]/div/div[1]/div/ul/li/a")
elem_select_service_moneyforwardme.click()
sleep(3)

elem_enter_moneyforwardme_use_account = browser.find_element(By.XPATH, "/html/body/main/div/div/div/div/div[1]/section/form/div[2]/div/div[2]/input")
elem_enter_moneyforwardme_use_account.click()
print(">>>> done!")
sleep(3)

print(">>>> enter the main page...")
elem_kakeibo = browser.find_element(By.XPATH, "//*[@id=\"header-container\"]/header/div[2]/ul/li[2]/a")
elem_kakeibo.click()
sleep(3)

print(">>>> enter the kakeibo page & select year and month...")
elem_select_year_and_month = browser.find_element(By.XPATH, "//*[@id=\"in_out\"]/div[2]/div/span")
elem_select_year_and_month.click()

actions = ActionChains(browser)
actions.move_to_element(browser.find_element(By.XPATH, f"//*[@id=\"in_out\"]/div[2]/div/div/div[{int(strftime('%Y'))-year+1}]"))
actions.move_to_element(browser.find_element(By.XPATH, f"//*[@id=\"in_out\"]/div[2]/div/div/div[{int(strftime('%Y'))-year+1}]/div/a[{month}]"))
actions.click()
actions.perform()
sleep(3)

print(">>>> downloading...")
elem_download_dropdown = browser.find_element(By.XPATH, "//*[@id=\"js-dl-area\"]/a")
elem_download_dropdown.click()
elem_dlcsv = browser.find_element(By.XPATH, "//*[@id=\"js-csv-dl\"]/a")
elem_dlcsv.click()
sleep(3)
print(">>>> OK!!")



print(">>>> every program completed")
browser.close()



#### スプレッドシートにcsvをアップロード ####
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("./credentials.json", scope)
gc = gspread.authorize(credentials)


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
