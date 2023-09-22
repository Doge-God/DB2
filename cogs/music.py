import datetime
import discord
from discord.ext import commands
import yt_dlp
import domain.data_manager as data_manager
from domain.data_manager import SongInfo
from discord import VoiceClient
from domain.enums import VC_STATE

#from main import join
from common import check_vc_command, join_voice_chan, disconnect_voice_chan

###############################################
############ DATA STRUCTURES ##################
###############################################

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

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn'
}

###############################################
############ HELPER FUNCTIONS #################
###############################################

def extract_yt_song_info(search_phrase) -> SongInfo:
    with yt_dlp.YoutubeDL(ytdl_format_options) as ytdl_obj:
        try:
            info = ytdl_obj.extract_info(str(search_phrase), download=False)['entries'][0]
        except Exception:
            info = ytdl_obj.extract_info(str(search_phrase), download=False)
        return SongInfo(info['formats'][7]['url'], info['title'], info['duration'])

def play_from_song_info(song_info:SongInfo, vc_client:VoiceClient):
    ffmpeg_options['options'] = f'-vn -ss {song_info.seek_sec}'
    vc_client.play(discord.FFmpegPCMAudio(song_info.source, **ffmpeg_options)
                , after = lambda err: print('Player error: %s' % err) if err else play_next(vc_client))

def play_next(vc_client:VoiceClient):
    server_song_queue = data_manager.get_data(vc_client.guild.id).song_queue
    server_song_queue.pop(0)
    if len(server_song_queue) == 0:
        print(str(vc_client.guild.id) + ": song queue empty.")
        return
    else:
        play_from_song_info(server_song_queue[0], vc_client)

def try_begin_play(vc_client:VoiceClient):
    server_song_queue = data_manager.get_data(vc_client.guild.id).song_queue
    if len(server_song_queue) == 1:
        play_from_song_info(server_song_queue[0], vc_client)

def get_eta_sec(que_pos:int, server_info):
    tot = 0
    for x in range(0, que_pos):
        tot += int(data_manager.get_data(server_info).song_queue[x].duration)
    return tot



###############################################
############ END POINTS #######################
###############################################

class music(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded music cog ... Complete")

    @commands.command()
    async def ping(self,ctx):
        await ctx.send("pong")
    
    @commands.command()
    async def play(self,ctx:commands.Context, *phrases):
        match check_vc_command(ctx):
            case VC_STATE.USER_NOT_IN_VC:
                await ctx.send("Join voice channel for voice channel commands.")
                return
            case VC_STATE.BOT_NOT_IN_SERVER:
                await join_voice_chan(ctx)
                return
            case VC_STATE.BOT_NOT_IN_CHANNEL:
                await join_voice_chan(ctx)
                return
            case VC_STATE.SAME_SERVER_CHANNEL:
                pass

        search_term = ' '.join(phrases)
        print("Searching term: " + search_term)
        found_song_info = extract_yt_song_info(search_term)

        server_song_queue = data_manager.get_data(ctx.guild.id).song_queue

        embedObj=discord.Embed(title="__{}__".format(found_song_info.title),color=discord.Color.teal())
        embedObj.set_author(name="Added to queue: ")
        embedObj.add_field(name="Position",value="#{}".format(len(server_song_queue)),inline=True)
        embedObj.add_field(name="Duration",value=str(datetime.timedelta(seconds=int(found_song_info.duration))),inline=True)
        embedObj.add_field(name="ETA"
            ,value=str(datetime.timedelta(seconds=get_eta_sec(len(server_song_queue),ctx))),inline=True)
        
        await ctx.send(embed=embedObj)

        server_song_queue.append(found_song_info)
        try_begin_play(data_manager.get_data(ctx.guild.id).vc_client)
    
    @commands.command()
    async def skip(self,ctx:commands.Context, tgt_track=None):
        match check_vc_command(ctx):
            case VC_STATE.USER_NOT_IN_VC:
                await ctx.send("Joing VC for VC commands.")
                return
            case VC_STATE.BOT_NOT_IN_SERVER:
                await ctx.send("DB2 not in vc in this server.")
                return
            case VC_STATE.BOT_NOT_IN_CHANNEL:
                await ctx.send("DB2 not in this channel.")
                return
            case VC_STATE.SAME_SERVER_CHANNEL:
                pass
        
        server_data = data_manager.get_data(ctx)
        song_queue = server_data.song_queue

        # skip the currently playing song
        if tgt_track == None:
            if len(song_queue) < 1:
                await ctx.send(embed=discord.Embed(title="Queue empty.",color=discord.Color.teal()))
                return
            else:
                server_data.vc_client.stop()
                await ctx.send(embed=discord.Embed(title="Skipped.",color=discord.Color.teal()))
                return

        track_num = int(tgt_track)
        embed_obj=discord.Embed(title="Removed:",color=discord.Color.teal())

        #trying to skip last added song AND theres more than 1 song in the queue
        if track_num == -1 and len(song_queue) > 1:
            embed_obj.add_field(name="#{}".format(len(song_queue)-1)
                +"   ({})".format(str(datetime.timedelta(seconds=int(song_queue[-1].duration))))
                ,value=song_queue[-1].title,inline=False)
            await ctx.send(embed=embed_obj)
            song_queue.pop(-1)
        
        elif track_num in range(1,len(song_queue)):
            embed_obj.add_field(name="#{}".format(track_num)
            +"   ({})".format(str(datetime.timedelta(seconds=int(song_queue[track_num].duration))))
            ,value=song_queue[track_num].title,inline=False)
            await ctx.send(embed=embed_obj)
            song_queue.pop(track_num)
        
        else:
            await ctx.send(embed=discord.Embed(title="Invalid skip location.",color=discord.Color.red()))

    @commands.command()
    async def queue(self,ctx:commands.Context):
        match check_vc_command(ctx):
            case VC_STATE.USER_NOT_IN_VC:
                await ctx.sent("Join VC for VC commands.")
                return
            case VC_STATE.BOT_NOT_IN_SERVER:
                await ctx.send("DB2 not in vc in this server.")
                return
            case VC_STATE.BOT_NOT_IN_CHANNEL:
                await ctx.send("DB2 not in this channel.")
                return
            case VC_STATE.SAME_SERVER_CHANNEL:
                pass
        
        server_data = data_manager.get_data(ctx)
        song_queue = server_data.song_queue

        if len(song_queue) == 0:
            await ctx.send(embed=discord.Embed(title="Queue empty.",color=discord.Color.teal()))
            return
        else:
            embed_obj=discord.Embed(title="Queue",color=discord.Color.teal())
            cnt = 0
            for song_info in song_queue:
                embed_obj.add_field(name= ("Currently playing:" if cnt == 0 else "#{}".format(cnt)) 
                + "   ({})".format(str(datetime.timedelta(seconds=int(song_info.duration))))
                ,value=song_info.title,inline=False)
                cnt += 1
            await ctx.send(embed=embed_obj)


        

async def setup(client):
    await client.add_cog(music(client))


