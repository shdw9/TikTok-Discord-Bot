import discord, json, requests,os, logging, asyncio
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

def checkURL(message):
    linkPrefixes = ['https://m.tiktok.com','https://vt.tiktok.com','https://tiktok.com','https://www.tiktok.com', 'https://vm.tiktok.com/']
    for link in linkPrefixes:
        if link in message:
            return True
    return False

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="LEAGUE OF LEGENDS"))
    print('=> Logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if "tiktok.com" in message.content:
        if (checkURL(message.content)):
            await message.add_reaction('🔁')
            fileName = message.content.split(".com/")[1].split('/')[0] + ".mp4"
            print("Getting TikTok id:" + message.content.split(".com/")[1].split('/')[0] + " ...")
            downloadLink = 'https://api.single-developers.software/tiktok?url=' + message.content
            r = requests.get(downloadLink)
            # print(r.json()["watermark"])
            
            downloadFile = requests.get(r.json()["watermark"])
            print('Downloading file ...')
            with open(fileName,'wb') as f:
                f.write(downloadFile.content)
            print('Finished downloading file!')

            if (os.path.getsize(fileName) >= 8388000):
                await message.add_reaction('❌')
                print("FILE IS TOO LARGE >:(")
                await message.channel.send(":x: Couldn't send the TikTok because the file was too large! [work in progress]")
                os.remove(fileName)
                return 

            print("Uploading ...")
            try:
                await message.channel.send(file=discord.File(fileName))
                await message.clear_reaction('🔁')
                await message.add_reaction('✅')
                print("Uploaded!")
            except Exception as e:
                await message.add_reaction('❌')
                print(e)
                await message.channel.send("Something went wrong! " + str(e))
            os.remove(fileName)

bot.run('')
