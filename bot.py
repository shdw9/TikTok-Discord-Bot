from discord.ext.commands import CommandNotFound
from bs4 import BeautifulSoup
import discord, requests, os, sys, traceback, json, asyncio, re, random, subprocess

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
    #print("getting video '" + url + "'")
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
                    if response.headers['location'] == '/en?err=url invalid!' or "url invalid" in response.headers['location']:
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

                        print("unknown resp head loc! : '" + response.headers["location"] + "'")
                        return {'valid': False,'error': 'unknownError'}

                else:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    for x in soup.findAll("a"):
                        if "href" in str(x) and "tiktokcdn.com" in x["href"]:
                            return {'valid':True,'is_video': True,'desc': soup.findAll('h2', attrs={'class':'white-text'})[0].get_text()[23:-19],'thumbnail': soup.findAll('img',attrs={'class':'responsive-img'})[0]['src'],'desc':soup.findAll('h2',class_="white-text")[1].getText(),'url': url,'items':x["href"]}

                    vids = []

                    for dlLink in soup.select('a[class*="btn waves-effect waves-light orange"]'):
                        if "href" in str(dlLink) and "https://" in str(dlLink):
                            vids.append(dlLink["href"])

                    if vids == []:
                        return {'valid': False,'error1': 'exception trying to find video link'}

                    return {
                        'valid': True,
                        'is_video': True,
                        'desc': soup.findAll('h2', attrs={'class':'white-text'})[0].get_text()[23:-19],
                        'thumbnail': soup.findAll('img',attrs={'class':'responsive-img'})[0]['src'],
                        'items': vids,
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

# Find parameter on url_site
def getParameter():

    # Variable
    token = ""

    # Get site of the url
    r = requests.get("https://snaptik.app")

    # Get soup
    soup = BeautifulSoup(r.text, "lxml")

    # Find token
    for el_input in soup.find_all("input"):
        if(el_input.get("name") == "token"):
            token = el_input.get("value")

    # Return cookie of the session
    return token

# Make request to site server
def make_req_server(token, url_video):

    # Header for request
    headers = {
        'authority': 'snaptik.app',
        'accept': '*/*',
        'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'dnt': '1',
        'origin': 'https://snaptik.app',
        'referer': 'https://snaptik.app/',
        'sec-ch-ua': '"Opera";v="99", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin'
    }

    # Make request to get data from site with parameter
    response = requests.get('https://snaptik.app/abc2.php', headers=headers, params = {
        'url': url_video,
        'token': token
    })

    # Return
    return response

# Exctact variable for decode from req_server
def extract_variable(response):

    # Find variable to send to decoder 
    list_var = re.findall(r'\(\".*?,.*?,.*?,.*?,.*?.*?\)', response.text)

    # Add to list variable
    res_input = []
    for e in (list_var[0].split(",")):
        res_input.append(str(e).replace("(", "").replace(")", "").replace('"', ""))

    # Return
    return res_input

# Call decoder to get response from page
def call_decoder(result_list_variable):

    attempts = 10
    # Call decoder in node js 
    while(True):
        if attempts == 0:
            print("error!")
            break
        try:
            output = subprocess.check_output([
                'node', 'decode.js',
                str(result_list_variable[0]), str(result_list_variable[1]), str(result_list_variable[2]), str(result_list_variable[3]), str(result_list_variable[4]), str(result_list_variable[5])
            ])
            break
        except:
            attempts -= 1


    # Get result from decoder
    result = (output).decode("utf-8") 

    return result

# Exract url of video with soup
def get_url_video(html_page):

    # Soup result -> (result is html page)
    soup_res = BeautifulSoup(html_page, "lxml")

    # Collect all url from soup
    url_download_video = ""
    for a in soup_res.find_all("a"):

        url = a.get("href")
        url = str(url).replace('\\', "").replace('"', "")

        if("snaptik" in url): 
            url_download_video = url

    return url_download_video


async def getPhotoInfo(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text,"html.parser")
    resp = json.loads(soup.find("script",id="__UNIVERSAL_DATA_FOR_REHYDRATION__").text)
    if "webapp.video-detail" not in resp["__DEFAULT_SCOPE__"]:
        print("webapp.video-detail not in vid",url)
        photoInfo = await getVideo(url)

        # snaptik
        token = getParameter()

        # Make req server 
        response = make_req_server(token = token, url_video = url)

        # Extract and get list of variable to decode
        result_list_variable = extract_variable(response)

        # Call decoder with list of variable
        html_response = call_decoder(result_list_variable)

        photoSoup = BeautifulSoup(html_response, "lxml")
        vidTitle = photoSoup.find("div",class_='\\"video-title\\"').text
        vidDesc = ""
        
        shareCover = photoInfo["items"][0]
        imagePosts = photoInfo["items"]
    else:
        vidDesc = resp["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["desc"]
        vidTitle = resp["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["imagePost"]["title"]
        shareCover = resp["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["imagePost"]["shareCover"]["imageURL"]["urlList"][0]
        imagePosts = resp["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["imagePost"]["images"]

    slideshowImages = []

    for x in imagePosts:
        if "imageURL" in x:
            slideshowImages.append(x["imageURL"]["urlList"][0])
        elif "tiktokcdn.com" in x:
            slideshowImages.append(x)

    if shareCover in slideshowImages:
        slideshowImages.remove(shareCover)

    return {"title":vidTitle,"desc":vidDesc,"cover":shareCover, "images":slideshowImages}


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if "tiktok.com" in message.content:

        hasUrl = False
        
        for domain in tikTokDomains:
            if domain in message.content.strip():
                hasUrl = True

        if hasUrl == False:
            return
            
        message.content = message.content.strip()
        
        await message.add_reaction('🔁')
        try:
            if (checkURL(message.content)):
                tikTok = await getVideo(message.content)
                
                if tikTok["valid"] != True:
                    print(tikTok)
                    await message.clear_reaction('🔁')
                    await message.add_reaction('👮‍♂️')
                    await message.add_reaction('🛑')
                    await message.add_reaction('🚷')
                    return

                tiktokDescription = tikTok["desc"].strip()

                description = message.author.mention 
                if not tiktokDescription == "":
                    description += "\n\n" + tiktokDescription
                description += "\n\n:link:: <"+message.content+">"

                if tikTok["is_video"] == False:
                    photoInfo = await getPhotoInfo(message.content)

                    #download cover photo
                    cover = requests.get(photoInfo["cover"])
                    with open("cover.jpeg","wb") as f:
                        f.write(cover.content)

                    msg = await message.channel.send(content=message.author.mention + "\n\n**" + photoInfo["title"] + "**\n" + photoInfo["desc"] + "\n\n:link:: <"+message.content+">",file=discord.File("cover.jpeg"))
                    if len(photoInfo["images"]) > 2:
                        thread = await msg.create_thread(name="**"+photoInfo["title"] + "**",auto_archive_duration=60)
                        for photo in photoInfo["images"]:
                            await thread.send(content=photo)
                        if photoInfo["desc"] == ":no_entry_sign:":
                            await thread.send(content=":warning: Could not get normal TikTok response structure. Could not get thumbnail, description, and images. :warning:")
                    else:
                        for photo in photoInfo["images"]:
                            await message.channel.send(content=photo)
                    os.remove("cover.jpeg")
                    
                    try:
                        await message.delete()
                    except:
                        await message.add_reaction('✅')
                        await message.clear_reaction('🔁')
                        await thread.send(content=photo)
                        await asyncio.sleep(1)
                    return
                
                # download file with randomized file name
                randomizedFileName = str(random.randint(10000000,90000000)) + ".mp4"
                
                # for each dl, try uploading
                for vid in tikTok["items"]:
                    attempts = 10
                    while(True):
                        if attempts == 0:
                            await message.channel.send(content="Failed to download TikTok! Try again in a few minutes.")
                            return
                        downloadFile = requests.get(vid)
                        with open(randomizedFileName,"wb") as f:
                            f.write(downloadFile.content)
                        if not os.path.getsize(randomizedFileName) < 5000:
                            break
                        attempts -= 1
                        print("failed to upload", os.path.getsize(randomizedFileName), downloadFile.status_code)

                    # attempt to upload the file, if not then the file size is over 8MB
                    try:
                        await message.channel.send(content=description,file=discord.File(randomizedFileName))
                        try:
                            await message.delete()
                        except:
                            await message.add_reaction('✅')
                            await message.clear_reaction('🔁')
                        return
                    except:
                        print("failed to upload vid url", vid)

                    os.remove(randomizedFileName)
                        
                print("file too large, proceeding with bitly url shortening")

                description = message.author.mention + "\n\n" + tiktokDescription + "\n\n:film_frames:: "
                # failed to upload any download variants, send link instead
                sentBackup = False
                for vid in tikTok["items"]:
                    if "akamaized.net" in vid:
                        sentBackup = True
                        await message.channel.send(description + vid.split("?")[0])
                        break
                
                if not sentBackup:
                    bitty = shortenURL(tikTok["items"][0])
                    await message.channel.send(description + bitty)

                try:
                    await message.delete()
                except:
                    await message.add_reaction('✅')
                    await message.clear_reaction('🔁')
                
        except Exception as e:
            print(traceback.format_exc())
            try:
                await message.clear_reaction('🔁')
            except:
                pass

bot.run(discordBotToken)
