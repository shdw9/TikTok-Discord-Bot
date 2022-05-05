# tiktok-discord-bot

Sends a TikTok video when a TikTok link is found. 

# Features

If the TikTok video size is below 8 MB, it will send the .mp4 as a file
<br>![cmdline](https://i.imgur.com/HzFCArM.png) 

If not, then the direct TikTok video URL will get shortened via bit.ly and Discord will still show the video embed
<br>![cmdline](https://i.imgur.com/e9NSCLt.png)

# How It Works

Discord Bot checks for all messages -> if message has tiktok.com -> <br>check if valid TikTok url -> get direct video link of TikTok -> <br>download the video using that link -> try to send that file <br>(if file is over 8mb, it will shorten the direct video link so it looks nice and the link will autoembed like YouTube videos on Discord)
