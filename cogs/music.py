import discord
from discord.ext import commands
import yt_dlp

ytdl_format_options = {
    'format': 'bestaudio/best',
    #'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0' 
}

class SongInfo():
    def __init__(self, source:str, title:str, duration:int):
        self.source = source
        self.title = title
        self.duration = duration

###############################################
############ END POINTS #######################
###############################################

class music(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded music cog ... Complete")

    @commands.command("ping")
    async def ping(self,ctx):
        await ctx.send("pong")

async def setup(client):
    await client.add_cog(music(client))

###############################################
############ HELPER FUNCTIONS #################
###############################################

def search_youtube(search_phrase):
    with yt_dlp.YoutubeDL(ytdl_format_options) as ytdl_obj:

        try:
            info = ytdl_obj.extract_info(str(search_phrase), download=False)['entries'][0]
        except Exception:
            info = ytdl_obj.extract_info(str(search_phrase), download=False)
            