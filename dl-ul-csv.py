import csv
import glob
import os
import re
import subprocess
import sys

# from webdriver_manager.chrome import ChromeDriverManager
from time import sleep, strftime

import gspread
from gspread.exceptions import APIError
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
options.add_argument("--window-size=1920,1080")
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

# 未捕捉例外で終了する際、原因調査用にスクリーンショットとページソースをdebug/へ保存する
def _save_debug_info_on_error(exc_type, exc_value, tb):
    try:
        os.makedirs("debug", exist_ok=True)
        timestamp = strftime("%Y%m%d-%H%M%S")
        browser.save_screenshot(f"debug/error-{timestamp}.png")
        with open(f"debug/error-{timestamp}.html", "w", encoding="utf-8") as f:
            f.write(browser.page_source)
        print(f">>>> saved debug info: debug/error-{timestamp}.png / .html")
    except Exception as save_error:
        print(f">>>> failed to save debug info: {save_error}")
    sys.__excepthook__(exc_type, exc_value, tb)


sys.excepthook = _save_debug_info_on_error

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

# グループの選択
print(">>>> select the group...")
elem_group = browser.find_element(By.XPATH, "//*[@id=\"group_id_hash\"]/option[2]")
elem_group.click()
sleep(3)

# 家計簿ページへ
print(">>>> enter the main page...")

# Brazeのin-app messageモーダルが出ていればDOMごと除去する（出ない場合はスキップ）
try:
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.ab-in-app-message"))
    )
    browser.execute_script(
        "document.querySelectorAll('.ab-iam-root, iframe.ab-in-app-message').forEach(e => e.remove())"
    )
    sleep(1)
except TimeoutException:
    pass

elem_kakeibo = browser.find_element(By.XPATH, "//*[@id=\"header-container\"]/header/div[2]/ul/li[2]/a")
elem_kakeibo.click()
sleep(3)

# 家計簿をダウンロードするために年月を指定する
print(f">>>> enter the kakeibo page & select {year}/{month}...")
wait = WebDriverWait(browser, 30)


def _current_period():
    return browser.find_element(By.CSS_SELECTOR, "#in_out .in-out-header-title").text


def _click(elem):
    """通常のクリックが他要素に遮られる場合はJavaScript経由でクリックする"""
    try:
        elem.click()
    except (ElementClickInterceptedException, ElementNotInteractableException):
        browser.execute_script("arguments[0].click();", elem)


# 年月選択のドロップダウンを開く
elem_select_year_and_month = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-uikit-year-month-select-dropdown"))
)
_click(elem_select_year_and_month)

# 対象の年月リンクをdata属性で直接指定してクリックする
# （マウス移動で選ぶ方式は、ドロップダウンの表示位置がずれると別の年月を選んでしまうため）
elem_month_link = wait.until(
    EC.presence_of_element_located(
        (
            By.CSS_SELECTOR,
            f".js-uikit-year-month-select-dropdown-link[data-year='{year}'][data-month='{month}']",
        )
    )
)
browser.execute_script("arguments[0].click();", elem_month_link)

# 指定した年月に切り替わるまで待つ（切り替わらなければここで失敗させる）
expected_period = f"{year}/{month:02d}/01"


def _is_expected_period(_driver):
    try:
        return expected_period in _current_period()
    except Exception:
        return False


try:
    wait.until(_is_expected_period)
except TimeoutException:
    raise RuntimeError(
        f"failed to select {expected_period} (current period: {_current_period()})"
    )
print(f">>>> selected period: {_current_period()}")
sleep(3)


# csvをダウンロード
print(">>>> downloading...")
csv_files_before = set(glob.glob("*.csv"))

try:
    elem_download_dropdown = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#js-dl-area .dropdown-toggle"))
    )
except TimeoutException:
    raise RuntimeError(
        f"download button is not available for {expected_period} "
        "(the selected month may have no data)"
    )
_click(elem_download_dropdown)

elem_dlcsv = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#js-csv-dl a")))
_click(elem_dlcsv)


# ダウンロード完了（新しいcsvが出現し、かつ未完了の.crdownloadが残っていない）を待つ
def _wait_for_downloaded_csv(timeout=60):
    for _ in range(timeout):
        downloaded = set(glob.glob("*.csv")) - csv_files_before
        if downloaded and not glob.glob("*.crdownload"):
            return sorted(downloaded)[0]
        sleep(1)
    return None


csv_file_name = _wait_for_downloaded_csv()
if csv_file_name is None:
    raise RuntimeError("csv download did not complete")

print(f">>>> downloaded: {csv_file_name}")
print(">>>> every program completed")
browser.close()


#### スプレッドシートにcsvをアップロード ####

# Google Sheets APIが一時的なエラー(5xx/レート制限)を返した場合、指数バックオフで再試行する
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def with_retry(func, *args, retries=5, base_delay=2, **kwargs):
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            status_code = getattr(e.response, "status_code", None)
            if status_code in RETRYABLE_STATUS_CODES and attempt < retries - 1:
                wait = base_delay * (2 ** attempt)
                print(f">>>> Sheets API {status_code}, retrying in {wait}s (attempt {attempt + 1}/{retries})...")
                sleep(wait)
                continue
            raise


scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("./credentials.json", scope)
gc = gspread.authorize(credentials)

spreadsheet_name = f"家計簿_{year}"
spreadsheet = with_retry(gc.open, spreadsheet_name)
worksheet = with_retry(spreadsheet.worksheet, f"{month}月")

with_retry(spreadsheet.values_clear, f"{month}月!Q1:Z200")
csv_list = list(csv.reader(open(csv_file_name, encoding="shift_jis")))

# csv.readerで読み込んだものは全て文字列となるため、金額部分のみint型に変更
for row in csv_list[1:]:
    row[3] = int(row[3])

with_retry(worksheet.update, "Q1:Z200", csv_list)
os.remove(f"{csv_file_name}")
