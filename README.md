# tiktok-discord-bot

Scrapes TikTok videos and photo slideshows using musicaldown & snaptik's API and uploads them on Discord. 

<br>Just post the TikTok link on a Discord channel and it'll automatically upload it for you.

# Features

If the TikTok video size is below 8 MB, it will upload the video on Discord
<br>![cmdline](https://i.imgur.com/gnyXzT4.png) 

If not, then it will try to upload **VARYING** video qualities, and if it still doesn't work then it will send the direct TikTok video url
<br>![cmdline](https://i.imgur.com/al60WA2.png)

Creates a message thread for TikTok slideshows if there are more than 3 photos
<br>![cmdline](https://i.imgur.com/CmTc7Vz.png) 

