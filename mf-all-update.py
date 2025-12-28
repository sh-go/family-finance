import re
import subprocess

# from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By

import settings

#### MoneyForwardの一括更新 ####
# 事前準備
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


# 家計簿グループ（すべての金融機関）を選択
print(">>>> select the group...")
elem_group = browser.find_element(By.XPATH, "//*[@id=\"group_id_hash\"]/option[3]")  
elem_group.click()
sleep(3)

# 一括更新を実行
print(">>>> start all update...")
elem_all_update = browser.find_element(By.XPATH, "//*[@id=\"registered-accounts\"]/div/div[2]/a")
elem_all_update.click()
sleep(3)

# 家計グループを選択
print(">>>> select the group...")
elem_group = browser.find_element(By.XPATH, "//*[@id=\"group_id_hash\"]/option[2]")
sleep(3)

# 更新ボタンをクリック後、discodeで通知
import discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
@client.event
async def on_ready(): 
    guild = discord.utils.get(client.guilds)
    channel = discord.utils.get(guild.text_channels, name="一般")
    await channel.send("一括更新が完了しました💹")
    await client.close()

client.run(settings.DISCODE_BOT_TOKEN_FAMILYFINANCE)