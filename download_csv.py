from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import subprocess, re, os

EMAIL = "alive.vb.s2@gmail.com"
PASSWORD = "money8003150"
TWO_STEP_AUTHENTICATION_CODE = "HWFAN5ZJ 2AV7RW5J CXGNND76 J5UCL6SZ OUZM4ZA5 VTZU7NDF PCH4EESP N73NLCNR PIQ52JLR CUFZY7BV"
# Moneyforward ID 復元コード:
# HWFAN5ZJ
# 2AV7RW5J
# CXGNND76
# J5UCL6SZ
# OUZM4ZA5
# VTZU7NDF
# PCH4EESP
# N73NLCNR
# PIQ52JLR
# CUFZY7BV

options = Options()
options.add_experimental_option("prefs", {
    "download.default_directory": os.getcwd() + "//download"
})
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument('--disable-blink-features=AutomationControlled')
service = ChromeService("/usr/bin/chromedriver") # ChromeDriverManager().install()を使いたい
browser = webdriver.Chrome(service=service, options=options)
browser.get("https://id.moneyforward.com/sign_in/email")

# メールアドレスを入力＆ログイン
elem_input_email = browser.find_element(By.XPATH, "/html/body/main/div/div/div/div[1]/div[1]/section/form/div[2]/div/input")
elem_input_email.send_keys(EMAIL)

elem_login = browser.find_element(By.XPATH, "/html/body/main/div/div/div/div[1]/div[1]/section/form/div[2]/div/div[3]/input")
elem_login.click()
sleep(3)

# パスワード入力＆ログイン
elem_input_password = browser.find_element(By.XPATH, "/html/body/main/div/div/div/div/div[1]/section/form/div[2]/div/input[2]")
elem_input_password.send_keys(PASSWORD)

elem_login2 = browser.find_element(By.XPATH, "/html/body/main/div/div/div/div/div[1]/section/form/div[2]/div/div[3]/input")
elem_login2.click()
sleep(3)

# 二段階認証
two_step_authentication = ["oathtool", "--totp", "--base32", TWO_STEP_AUTHENTICATION_CODE]
auth_code = re.findall(r'\d+', subprocess.check_output(two_step_authentication).decode("utf-8"))

elem_input_authcode = browser.find_element(By.XPATH, "/html/body/main/div/div/div/section/div[1]/section/form/div[2]/div/div[1]/input")
elem_input_authcode.send_keys(auth_code[0])

elem_login3 = browser.find_element(By.XPATH, "/html/body/main/div/div/div/section/div[1]/section/form/div[2]/div/div[2]/input")
elem_login3.click()
sleep(3)

# マネーフォワードMEのTOPページへ
elem_enter_moneyforwardme = browser.find_element(By.XPATH, "/html/body/main/div/div[2]/div/div[1]/div/ul/li/a")
elem_enter_moneyforwardme.click()
sleep(3)

elem_kakeibo = browser.find_element(By.XPATH, "//*[@id=\"header-container\"]/header/div[2]/ul/li[2]/a")
elem_kakeibo.click()
sleep(3)

elem_dlcsv = browser.find_element(By.XPATH, "//*[@id=\"js-dl-area\"]/a")
elem_dlcsv.click()
elem_dlcsv_dropdown = browser.find_element(By.XPATH, "//*[@id=\"js-dl-area\"]/ul/li[1]")
elem_dlcsv_dropdown.click()
