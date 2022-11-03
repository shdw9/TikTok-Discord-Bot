from discord.ext import commands
from discord.ext.commands import CommandNotFound
from httpx import AsyncClient
from re import findall
import discord, requests, os, sys

sys.path.append("./libs/")

bot = commands.Bot(command_prefix='!')

###
userAgent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"
bitlyUsername = ""
bitlyPassword = ""
discordBotToken = ""
###

tikTokDomains = (
    'http://vt.tiktok.com', 'http://app-va.tiktokv.com', 'http://vm.tiktok.com', 'http://m.tiktok.com', 'http://tiktok.com', 'http://www.tiktok.com', 'http://link.e.tiktok.com', 'http://us.tiktok.com',
    'https://vt.tiktok.com', 'https://app-va.tiktokv.com', 'https://vm.tiktok.com', 'https://m.tiktok.com', 'https://tiktok.com', 'https://www.tiktok.com', 'https://link.e.tiktok.com', 'https://us.tiktok.com'
)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name="shdw's Tiktoks", url='https://www.twitch.tv/bikinis'))
    print('=> Logged in as {0.user}'.format(bot))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

async def getVideo(url):
    video_id_from_url=findall('https://www.tiktok.com/@.*?/video/(\d+)', url)
    if len(video_id_from_url)>0:
        video_id=video_id_from_url[0]
    else:
        headers1 = {
            "User-Agent": userAgent,
            "Accept": "text/html, application/xhtml+xml, application/xml; q=0.9, image/avif, image/webp, */*; q=0.8"
        }

        async with AsyncClient() as client:
            r1 = await client.get(url, headers=headers1)
        #print("r1", r1.status_code)
        if r1.status_code ==301:
            video_id = findall('a href="https://www.tiktok.com/@.*?/video/(\d+)', r1.text)[0]
        #403
        else:
            video_id = findall("video&#47;(\d+)", r1.text)[0]

    url2 = f"http://api16-normal-useast5.us.tiktokv.com/aweme/v1/aweme/detail/?aweme_id={video_id}"
    headers2 = {
        "User-Agent": userAgent}
    async with AsyncClient() as client:
        r2 = await client.get(url2, headers=headers2)
    #print("r2", r2.status_code)
    resp = r2.json()

    try:
        is_video = len(resp["aweme_detail"]["video"]["bit_rate"]) > 0
    except:
        #video unavailable
        return {"valid":False}

    #print("is_video", is_video)

    nickname = resp["aweme_detail"]["author"]["nickname"]
    desc = resp["aweme_detail"]["desc"]
    statistic = resp["aweme_detail"]["statistics"]
    music = resp["aweme_detail"]["music"]["play_url"]["uri"]
    if is_video:
        cover_url = resp["aweme_detail"]["video"]["origin_cover"]["url_list"][0]

        for bit_rate in resp["aweme_detail"]["video"]["bit_rate"]:
            height=bit_rate["play_addr"]["height"]
            width=bit_rate["play_addr"]["width"]
            data_size=bit_rate["play_addr"]["data_size"]

            url_list=bit_rate["play_addr"]["url_list"]
            quality_type=bit_rate["quality_type"]

            if int(data_size)>19999999:
                print("to_large_for_tg",height,"x",width,int(data_size)/1000000,"MB","quality_type:",quality_type)
            else:
                #print("good_for_tg",height,"x",width,int(data_size)/1000000,"MB","quality_type:",quality_type)
                videos_url=url_list
                large_for_tg=False
                break
        else:
            videos_url = resp["aweme_detail"]["video"]["bit_rate"][0]["play_addr"]["url_list"][-1]
            large_for_tg=True
        return {"valid": True, "is_video": True, "large_for_tg": large_for_tg, "cover": cover_url, "items": videos_url, "nickname": nickname, "desc": desc, "statistic": statistic, "music": music}

    else:
        images_url = []
        images = resp["aweme_detail"]["image_post_info"]["images"]
        for i in images:
            if len(i["display_image"]["url_list"]) > 0:
                images_url.append(i["display_image"]["url_list"][0])
            else:
                print("err. images_url 0 len")
        return {"valid": True, "is_video": False, "large_for_tg": False, "cover": None, "items": images_url, "nickname": nickname, "desc": desc, "statistic": statistic, "music": music}

def shortenURL(url):
    try:
        auth_res = requests.post("https://api-ssl.bitly.com/oauth/access_token", auth=(bitlyUsername, bitlyPassword))
        access_token = auth_res.content.decode()
        headers = {"Authorization": f"Bearer {access_token}"}
        groups_res = requests.get("https://api-ssl.bitly.com/v4/groups", headers=headers)
        groups_data = groups_res.json()['groups'][0]
        guid = groups_data['guid']
        shorten_res = requests.post("https://api-ssl.bitly.com/v4/shorten", json={"group_guid": guid, "long_url": url}, headers=headers)
        link = shorten_res.json().get("link")
        return link
    except:
        return url

def checkURL(message):
    for link in tikTokDomains:
        if link in message:
            return True
    return False

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if "tiktok.com" in message.content:
        await message.add_reaction('🔁')
        try:
            if (checkURL(message.content)):
                tikTok = await getVideo(message.content)
                
                if tikTok["valid"] != True:
                    await message.clear_reaction('🔁')
                    await message.add_reaction('🚷')
                    return

                directLink = tikTok["items"]
                tiktokDescription = tikTok["desc"].strip()

                description = message.author.mention 
                if not tiktokDescription == "":
                    description += "\n\n" + tiktokDescription
                description += "\n\n:link:: <"+message.content+">"

                if tikTok["is_video"] == False:
                    await message.channel.send(content=description + "\n" + message.content)
                    for photo in tikTok["items"]:
                        await message.channel.send(content=photo)
                    return
                
                # download file with randomized file name
                randomizedFileName = requests.get("https://random-word-api.herokuapp.com/word").json()[0] + ".mp4"
                downloadFile = requests.get(directLink[-1]).content
                with open(randomizedFileName,"wb") as f:
                    f.write(downloadFile)

                # attempt to upload the file, if not then the file size is over 8MB, return shortened bit.ly link
                try:
                    await message.channel.send(content=description,file=discord.File(randomizedFileName))
                except:
                    try:
                        bitty = shortenURL(directLink)
                        await message.channel.send(description + "\n\n"+ bitty)
                    except:
                        await message.channel.send(content=description + "\n" + directLink[-1])

                try:
                    await message.delete()
                except:
                    await message.add_reaction('✅')
                    await message.clear_reaction('🔁')
                os.remove(randomizedFileName)
        except Exception as e:
            print(e)
            try:
                await message.clear_reaction('🔁')
            except:
                pass


bot.run(discordBotToken)
