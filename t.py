from discord.ext import tasks
from cgi import test
from datetime import datetime
from xmlrpc.client import DateTime
import discord
from discord.ext import commands
import os
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time

import requests

import gspread 
from oauth2client.service_account import ServiceAccountCredentials



#크롬드라이버옵션
options = webdriver.ChromeOptions()
options.add_argument("headless")


# -------    스프레드시트 접속관련 
scope = [
'https://spreadsheets.google.com/feeds',
'https://www.googleapis.com/auth/drive',
]

json_file_name = 'archeage-353016-423372f38f09.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)
spreadsheet_url_test = 'https://docs.google.com/spreadsheets/d/1jhI4c4oBtCwCOwiOQLdKTy52gUbpJqYvaqz_Daacozs/edit#gid=0'

spreadsheet_url='https://docs.google.com/spreadsheets/d/1b7JcFtKMkVbwt9_cMKk7SG_q-cfx6WJHIsGqNTlgf8M/edit#gid=0'

spreadsheet_raid ='https://docs.google.com/spreadsheets/d/1kSnC8_FerZzHlmxEatPrhKZPLv5jiujJFTOggJTobcE/edit#gid=0'

# 스프레스시트 문서 가져오기 
doc = gc.open_by_url(spreadsheet_url)
doc1 = gc.open_by_url(spreadsheet_url_test)
doc2 = gc.open_by_url(spreadsheet_raid)

# 시트 선택하기
worksheet = doc.worksheet('시트1')
worksheet1 = doc1.worksheet('시트1')
worksheet2 = doc2.worksheet('시트1')
now = str(datetime.now())

bot = commands.Bot(command_prefix='$')

savedate = ''

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot)) #봇이 실행되면 콘솔창에 표시
    await bot.change_presence(status=discord.Status.online,activity=discord.Game('$신청 직업군 가능직업 장점 보유전차'))
    

@bot.event
async def on_message(ctx):
    global savedate
    global now
    now = str(datetime.now())
    dayCheck = f'{datetime.today().month}-{datetime.today().day}'
    if ctx.author == bot.user: # 봇 자신이 보내는 메세지는 무시
        return

    if dayCheck != savedate :
        print("update spreadsheet")
        every_day_checkscore(datetime.today())
        savedate = dayCheck

    #if ctx.channel.id == 985201371819147344 and ctx.content.startswith('$'):
    if  ctx.content.startswith('$'):
        await bot.process_commands(ctx) 

@bot.command()
async def 신청(ctx):
    if ctx.channel.id == 985201371819147344:
        userName = ctx.author.nick
        msg = ctx.message.content.split(' ',maxsplit=10)
        idx1 = userName.find('[')
        idx2 = userName.find(']')
        if len(msg) == 3 :
            msg.append("-")
        if len(msg) == 4 :
            msg.append("-")
        worksheet.append_row([now,userName[idx2+1:].strip(),userName[idx1+1:idx2].strip(),'참석',msg[1],msg[2],msg[3] ,msg[4]])
        await ctx.message.add_reaction('👍')

@bot.command()
async def 장비점수시트(ctx):
    await ctx.channel.send("https://docs.google.com/spreadsheets/d/1jhI4c4oBtCwCOwiOQLdKTy52gUbpJqYvaqz_Daacozs/edit?usp=sharing")

@bot.command()
async def 목록(ctx):
    idx = 1
    # 아이디 ( 2열 )
    columns1 = worksheet1.col_values(2)
    # 최근점수 ( 3열 )
    columns2 = worksheet1.col_values(3)

    if len(columns2) < len(columns1) : 
        for i in range(len(columns1)-len(columns2)) :
            columns2.append("-")

    ### embed
    embed=discord.Embed(color=0x7FFFD4)
    embed.add_field(name=f":: 장비점수 확인 리스트 | $갱신 = Last ",value=f"$검색/추가/삭제 아이디",inline=False)
    for i in columns1 :
        if i == "닉네임":
            continue
        if len(columns2[idx]) < 1 :
            columns2[idx] = "-"
        embed.add_field(name=f"{i}",value= f"{columns2[idx]}",inline=True)
        idx += 1

    embed.set_footer(text="requested by: {}".format(ctx.author.display_name))
    ### need permissions to delete message
    #await ctx.message.delete()
    await ctx.channel.send(embed=embed)

@bot.command()
async def 검색(ctx):

    targetId = ctx.message.content.split(' ',maxsplit=2)[1]
    try:
        idxN = 0
        header = worksheet1.row_values(1)
        value = worksheet1.row_values(worksheet1.find(targetId).row)
        print(value)
        if len(value) < len(header) :
            gp = len(header)-len(value)
            temp_list = []

            for i in value:
                print(len(i))
                if len(i) < 1:
                    temp = i.replace("","-")
                    temp_list.append(temp)
                else:
                    temp_list.append(i)
            for i in range(gp):
                temp_list.append("-")
            value = temp_list
        else: 
            temp_list = []
            for i in value:
                print(len(i))
                if len(i) < 1:
                    temp = i.replace("","-")
                    temp_list.append(temp)
                else:
                    temp_list.append(i)
            value = temp_list

        ### embed
        embed=discord.Embed(color=0x7FFFD4)
        embed.add_field(name=f":: {value[1]}",value=f"{value[0]}",inline=False)
        for i in header :
            if idxN <2:
                idxN+=1
                continue
            if len(value[idxN]) == 0 :
                value[idxN] == "-"
            embed.add_field(name=f"{i}",value= f"{value[idxN]}",inline=True)
            idxN+=1

        embed.set_footer(text="requested by: {}".format(ctx.author.display_name))

        ### embed2
        embed2 = discord.Embed(color=0x7000D4)
        embed2.add_field(name=f":: {value[1]}",value=f"{value[0]}",inline=False)
        for i in header[24:] :
            if idxN <25:
                idxN+=1
                continue
            if len(value[idxN]) == 0 :
                value[idxN] == "-"
            embed2.add_field(name=f"{i}",value= f"{value[idxN]}",inline=True)
            idxN+=1

        embed2.set_footer(text="requested by: {}".format(ctx.author.display_name))
        ### need permissions to delete message
        #await ctx.message.delete()
        await ctx.channel.send(embed=embed)
        await ctx.channel.send(embed=embed2)
    except:
        await ctx.channel.send(targetId + " 는  > $목록 < 에 없음")

@bot.command()
async def 추가(ctx):
    add_userId = ctx.message.content.split(' ',maxsplit=2)[1]
    columns = worksheet1.col_values(2)

    if add_userId in columns : 
        await ctx.channel.send(add_userId + " 는 이미 등록 되어있음")
        return

    driver = webdriver.Chrome('./chromedriver', options=options)
    urlPage = "https://archeage.xlgames.com/search?dt=characters&keyword={}&subDt=&server=EVERNIGHT".format(add_userId)
    driver.get(urlPage)
    time.sleep(1)

    htmlData = driver.page_source
    soup = BeautifulSoup(htmlData, 'html.parser')
    searchPage = soup.select_one('.character_card > a > .character_name')
    user_uuid = searchPage.attrs.get('data-uuid')

    worksheet1.append_row([user_uuid,add_userId])
    driver.quit()
    await ctx.message.add_reaction('👌')

@bot.command()
async def 삭제(ctx):
    targetId = ctx.message.content.split(' ',maxsplit=2)[1]
    columns = worksheet1.col_values(2)
    if targetId in columns :
        worksheet1.delete_row(worksheet1.find(targetId).row)
        await ctx.message.add_reaction('👌')
    else :
        await ctx.channel.send(targetId + " 는  > $목록 < 에 없음")

@bot.command()
async def 갱신(ctx):
    driver = webdriver.Chrome('./chromedriver', options=options)
    rows = worksheet1.col_values(1)
    dataList = []
    # 데이터 가져오기
    for i in rows :
        if i == "코드":
            continue
        userUrl = requests.get('https://archeage.xlgames.com/characters/'+i)
        soup = BeautifulSoup(userUrl.content, 'html.parser')
        cName = soup.find("a",{"class":"character_name"}).text.strip()
        score = soup.find("span",{"class":"score"}).text.strip()
        dataList.append([cName,score])
    # 스프레드 시트에 업데이트    
    for i in dataList :
        targetRow = worksheet1.find(i[0]).row
        print(i[1])
        worksheet1.update(f'C{targetRow}',i[1])

    print(dataList)
    driver.quit()
    await ctx.message.add_reaction('🎵')


#자동 업데이트
def every_day_checkscore(day):
    today = f'{day.month} - {day.day}'
    rows = worksheet1.col_values(1)
    dataList = []

    
    ## 헤더에 추가
    header = worksheet1.row_values(1)

    if today in header :
        print("already done")
        return
    rowCell = chr(len(header)+65)
    print(rowCell)
    worksheet1.update(f'{rowCell}1',today)

    driver = webdriver.Chrome('./chromedriver', options=options)
    # 데이터 가져오기

    for i in rows :
        if i == "코드":
            continue
        userUrl = requests.get('https://archeage.xlgames.com/characters/'+i)
        soup = BeautifulSoup(userUrl.content, 'html.parser')
        cName = soup.find("a",{"class":"character_name"}).text.strip()
        score = soup.find("span",{"class":"score"}).text.strip()
        dataList.append([cName,score])



    # 스프레드 시트에 업데이트    
    for i in dataList :
        targetRow = worksheet1.find(i[0]).row
        worksheet1.update(f'{rowCell}{targetRow}',i[1])

    
    print('Done')
    driver.quit()


@bot.command()
async def 참가(ctx):
    if ctx.channel.id == 996732982176006164 :
        userName = ctx.author.nick
        msg = ctx.message.content.split(' ',maxsplit=4)
        idx1 = userName.find('[')
        idx2 = userName.find(']')
        if len(msg) == 1 :
            msg.append("-")
        if len(msg) == 2 :
            msg.append("-")
        raid = f"{msg[1][0]}공대"
        worksheet2.append_row([now,userName[idx2+1:].strip(),userName[idx1+1:idx2].strip(),raid,msg[2]])
        print([now,userName[idx2+1:].strip(),userName[idx1+1:idx2].strip(),msg[1],msg[2]])
        await ctx.message.add_reaction('🎵')


bot.run('OTg1MjEwNzg5NTcwOTY1NTk0.Gbr3uz.frkDK7eiWQ0B-utHHrp1VKrT7oD9hATNXqrUxI')