import discord, gspread
import requests, os
import settings
from pdf2image import convert_from_path
from oauth2client.service_account import ServiceAccountCredentials


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

print("----- maked credentials.json ------" if os.path.isfile("./credentials.json") else "ないよ！")
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("./credentials.json", scope)
gc = gspread.authorize(credentials)


spreadsheet_name = "家計簿_2023"
spreadsheet = gc.open(spreadsheet_name)
spreadsheet_url = "https://docs.google.com/spreadsheets/d/" + spreadsheet.id
spreadsheet_url_options = (
    "/export?format=pdf" +
    "&gid=2090432382" +
    "&range=B1:J37" +
    "&portrait=true" +
    "&size=a5" +
    "&fitw=true" +
    "&horizontal_alignment=CENTER" +
    "&top_margin=0.00"
    "&bottom_margin=0.00"
    "&left_margin=0.00"
    "&right_margin=0.00"
    "&scale=4"
)


'''
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


@client.event
async def on_message(message):
    if message.author == client.user:
        if "家計簿" in message.content:
            
            # pdfを取得
            pdf_export_url = spreadsheet_url + spreadsheet_url_options
            pdf_name = "output.pdf"
            headers = {'Authorization': 'Bearer ' + credentials.create_delegated("").get_access_token().access_token}
            res = requests.get(pdf_export_url, headers=headers)
            with open(pdf_name, mode="wb") as f:
                f.write(res.content)

            # 取得したpdfを画像に変換
            image = convert_from_path(pdf_name)
            image[0].save("output.png", "png")

            await message.channel.send("お疲れさまでしたー！", file=discord.File("output.png"))
            

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds)
    channel = discord.utils.get(guild.text_channels, name="一般")
    await channel.send("先月の家計簿でーす！")
    
print("------ 実行されてます！ ------")


client.run(settings.DISCODE_BOT_TOKEN_FAMILYFINANCE)
