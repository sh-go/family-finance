import discord
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials
from pdf2image import convert_from_path

import settings

# 欲しい家計簿の年月を指定
year, month = map(int, input().split())

scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("./credentials.json", scope)
gc = gspread.authorize(credentials)

spreadsheet_name = f"家計簿_{year}"
spreadsheet = gc.open(spreadsheet_name)
spreadsheet_url = "https://docs.google.com/spreadsheets/d/" + spreadsheet.id
spreadsheet_url_options_for_monthly = (
    "/export?format=pdf" +
    f"&gid={spreadsheet.worksheet(f'{month}月').id}" +
    "&range=B1:J37" +
    "&portrait=true" +
    "&size=a5" +
    "&fitw=true" +
    "&horizontal_alignment=CENTER" +
    "&top_margin=0.05" +
    "&bottom_margin=0.05" +
    "&left_margin=0.01" +
    "&right_margin=0.01" +
    "&scale=4"
)
spreadsheet_url_options_for_special_expence = (
    "/export?format=pdf" +
    f"&gid={spreadsheet.worksheet(f'{month}月').id}" +
    "&range=L1:N37" +
    "&portrait=true" +
    "&size=a5" +
    "&fitw=true" +
    "&horizontal_alignment=CENTER" +
    "&top_margin=0.01" +
    "&bottom_margin=0.01" +
    "&left_margin=0.01" +
    "&right_margin=0.01" +
    "&scale=4"
)
spreadsheet_url_options_for_budget = (
    "/export?format=pdf" +
    f"&gid={spreadsheet.worksheet('年間予算').id}" +
    "&range=A2:T30" +
    "&portrait=false" +
    "&size=a5" +
    "&fitw=true" +
    "&horizontal_alignment=CENTER" +
    "&vertical_alignment=MIDDLE" +
    "&top_margin=0.01" +
    "&bottom_margin=0.01" +
    "&left_margin=0.01" +
    "&right_margin=0.01" +
    "&scale=4"
)


''' spreadsheetのformat設定一覧
    &format=pdf                   //export format
    &size=a4                      //A3/A4/A5/B4/B5/letter/tabloid/legal/statement/executive/folio
    &portrait=false               //true= Potrait / false= Landscape
    &scale=1                      //1= Normal 100% / 2= Fit to width / 3= Fit to height / 4= Fit to Page
    &top_margin=0.00              //All four margins must be set!
    &bottom_margin=0.00           //All four margins must be set!
    &left_margin=0.00             //All four margins must be set!
    &right_margin=0.00            //All four margins must be set!
    &gridlines=false              //true/false
    &printnotes=false             //true/false
    &pageorder=2                  //1= Down, then over / 2= Over, then down
    &horizontal_alignment=CENTER  //LEFT/CENTER/RIGHT
    &vertical_alignment=TOP       //TOP/MIDDLE/BOTTOM
    &printtitle=false             //true/false
    &sheetnames=false             //true/false
    &fzr=false                    //true/false
    &fzc=false                    //true/false
    &attachment=false             //true/false
'''


# discode.pyを使ってスプレッドシートを切り取り、画像として送信
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# botが準備できた段階で画像送信のon_messageを発火させるコメントを送信
@client.event
async def on_ready(): 
    guild = discord.utils.get(client.guilds)
    channel = discord.utils.get(guild.text_channels, name="一般")
    await channel.send(f"{year}年{month}月の家計簿です💴")


# 画像送信
@client.event
async def on_message(message): 
    if message.author == client.user:
        if "家計簿" in message.content:
            # pdfを取得
            headers = {'Authorization': 'Bearer ' + credentials.create_delegated("").get_access_token().access_token}
            res_1 = requests.get(spreadsheet_url + spreadsheet_url_options_for_monthly, headers=headers)
            res_2 = requests.get(spreadsheet_url + spreadsheet_url_options_for_special_expence, headers=headers)
            res_3 = requests.get(spreadsheet_url + spreadsheet_url_options_for_budget, headers=headers)
            
            with open("output_1.pdf", mode="wb") as f:
                f.write(res_1.content)
            with open("output_2.pdf", mode="wb") as f:
                f.write(res_2.content)
            with open("output_3.pdf", mode="wb") as f:
                f.write(res_3.content)
            
            # 取得したpdfを画像に変換
            image_1 = convert_from_path("output_1.pdf")
            image_2 = convert_from_path("output_2.pdf")
            image_3 = convert_from_path("output_3.pdf")
            image_1[0].save("output_1.png", "png")
            image_2[0].save("output_2.png", "png")
            image_3[0].save("output_3.png", "png")
            
            send_files = [
                discord.File("output_1.png"),
                discord.File("output_2.png"),
                discord.File("output_3.png"),
            ]
            
            await message.channel.send(files=send_files)
            await client.close()
            
            
client.run(settings.DISCODE_BOT_TOKEN_FAMILYFINANCE)