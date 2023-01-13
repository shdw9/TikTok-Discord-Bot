from discord.ext.commands import CommandNotFound
from bs4 import BeautifulSoup
import discord, requests, os, sys

sys.path.append("./libs/")

bot = discord.Bot(intents=discord.Intents.all())

###
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
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

def getToken(url):
    try:
        response = requests.post('https://musicaldown.com/', headers={"user-agent":userAgent})
        
        cookies = response.cookies
        soup = BeautifulSoup(response.content, 'html.parser').find_all('input')

        data = {
            soup[0].get('name'):url,
            soup[1].get('name'):soup[1].get('value'),
            soup[2].get('name'):soup[2].get('value')
        }
        
        return True, cookies, data
    
    except Exception:
        return None, None, None

async def getVideo(url):
    # credits to developedbyalex
    if not url.startswith('http'):
        url = 'https://' + url

    if url.lower().startswith(tikTokDomains):
        url = url.split('?')[0]
        
        status, cookies, data = getToken(url)

        if status:
            headers = {
                'Cookie': f"session_data={cookies['session_data']}",
                'User-Agent': userAgent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': '96',
                'Origin': 'https://musicaldown.com',
                'Referer': 'https://musicaldown.com/en/',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Te': 'trailers'
            }

            try:
                response = requests.post('https://musicaldown.com/download', data=data, headers=headers, allow_redirects=False)

                if 'location' in response.headers:
                    if response.headers['location'] == '/en/?err=url invalid!':
                        return {'valid': False,'error': 'invalidUrl'}

                    elif response.headers['location'] == '/en/?err=Video is private!':
                        return {'valid': False,'error': 'privateVideo'}

                    elif response.headers['location'] == '/mp3/download':
                        response = requests.post('https://musicaldown.com//mp3/download', data=data, headers=headers)
                        soup = BeautifulSoup(response.content, 'html.parser')

                        return {
                            'valid': True,
                            'type': 'audio',
                            'description': soup.findAll('h2', attrs={'class':'white-text'})[0].get_text()[13:],
                            'thumbnail': None,
                            'items': soup.findAll('a',attrs={'class':'btn waves-effect waves-light orange download'})[0]['href'],
                            'description':soup.findAll('h2',class_="white-text")[1].getText(),
                            'url': url
                        }

                    elif response.headers['location'] == '/photo/download':
                        response = requests.post('https://musicaldown.com//photo/download', data=data, headers=headers)
                        soup = BeautifulSoup(response.content, 'html.parser')

                        #print(soup.text)
                        photosList = []

                        for x in soup.findAll('div',class_="col s12 m3"):
                            photosList.append(str(x).split("<img")[1].split("src=\"")[1].split("\"")[0])

                        return {
                            #photo
                            'valid': True,
                            'is_video': False,
                            'link': "tiktok.com",
                            'items': photosList,
                            'desc': "**TIKTOK PHOTO SLIDESHOW**",
                            'url':url
                        }

                    else:
                        return {'valid': False,'error': 'unknownError'}

                else:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    for x in soup.findAll("a"):
                        if "href" in str(x) and "tiktokcdn.com" in x["href"]:
                            return {'valid':True,'is_video': True,'desc': soup.findAll('h2', attrs={'class':'white-text'})[0].get_text()[23:-19],'thumbnail': soup.findAll('img',attrs={'class':'responsive-img'})[0]['src'],'desc':soup.findAll('h2',class_="white-text")[1].getText(),'url': url,'items':x["href"]}


                    return {
                        'valid': True,
                        'is_video': True,
                        'desc': soup.findAll('h2', attrs={'class':'white-text'})[0].get_text()[23:-19],
                        'thumbnail': soup.findAll('img',attrs={'class':'responsive-img'})[0]['src'],
                        'items': soup.findAll('a',attrs={'class':'btn waves-effect waves-light orange'})[0]['href'],
                        'desc':soup.findAll('h2',class_="white-text")[1].getText(),
                        'url': url
                    }

            except Exception as e:
                print(e)
                return {'valid': False,'error1': 'exception'}
        
        else:
            return {'valid': False,'error2': 'exception'}

    else:
        return {'valid': False,'error': 'invalidUrl'}

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
                    await message.add_reaction('👮‍♂️')
                    await message.add_reaction('🛑')
                    await message.add_reaction('🚷')
                    return

                directLink = tikTok["items"]
                tiktokDescription = tikTok["desc"].strip()

                description = message.author.mention 
                if not tiktokDescription == "":
                    description += "\n\n" + tiktokDescription
                description += "\n\n:link:: <"+message.content+">"

                if tikTok["is_video"] == False:
                    await message.channel.send(content=message.author.mention + "\n\n:link:: <"+message.content+">")
                    for photo in tikTok["items"]:
                        await message.channel.send(content=photo)
                    try:
                        await message.delete()
                    except:
                        await message.add_reaction('✅')
                        await message.clear_reaction('🔁')
                    return
                
                # download file with randomized file name
                print(directLink)
                randomizedFileName = requests.get("https://random-word-api.herokuapp.com/word").json()[0] + ".mp4"
                
                attempts = 10
                while(True):
                    if attempts == 0:
                        await message.channel.send(content="Failed to download TikTok! Try again in a few minutes.")
                        return
                    downloadFile = requests.get(directLink)
                    with open(randomizedFileName,"wb") as f:
                        f.write(downloadFile.content)
                    if not os.path.getsize(randomizedFileName) < 5000:
                        break
                    attempts -= 1
                    print("failed to upload",os.path.getsize(randomizedFileName),downloadFile.status_code)

                # attempt to upload the file, if not then the file size is over 8MB, return shortened bit.ly link
                try:
                    await message.channel.send(content=description,file=discord.File(randomizedFileName))
                except:
                    try:
                        bitty = shortenURL(directLink)
                        await message.channel.send(description + "\n\n"+ bitty)
                    except:
                        pass

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
