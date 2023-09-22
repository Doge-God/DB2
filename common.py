
from domain.enums import VC_STATE
from discord.ext import commands
import domain.data_manager as data_manager

def check_vc_command(ctx : commands.Context):
    #check if user is in vc
    if not ctx.author.voice:
        return VC_STATE.USER_NOT_IN_VC
    
    #check if bot is in vc in current server
    if data_manager.get_data(ctx.guild.id).vc_client == None:
        return VC_STATE.BOT_NOT_IN_SERVER
    
    #bot is not in the same channel of the user
    if ctx.author.voice.channel.id != data_manager.get_data(ctx.guild.id).vc_client.channel.id:
        return VC_STATE.BOT_NOT_IN_CHANNEL
    
    return VC_STATE.SAME_SERVER_CHANNEL


async def join_voice_chan(ctx:commands.Context):
    match check_vc_command(ctx):
        case VC_STATE.USER_NOT_IN_VC:
            await ctx.send("Join VC for VC command.")
        case VC_STATE.BOT_NOT_IN_SERVER:
            new_vc_client = await ctx.message.author.voice.channel.connect()
            data_manager.get_data(ctx).vc_client = new_vc_client
            print("Joind vc, session ID: " + new_vc_client.session_id)
        case VC_STATE.BOT_NOT_IN_CHANNEL:
            await data_manager.get_data(ctx).vc_client.move_to(ctx.author.voice.channel)

async def disconnect_voice_chan(ctx:commands.Context):
    match check_vc_command(ctx):
        case VC_STATE.USER_NOT_IN_VC:
            await ctx.send("Join voice channel for voice channel commands.")
        case VC_STATE.BOT_NOT_IN_SERVER:
            await ctx.send("DB2 not in vc in this server.")
        case VC_STATE.BOT_NOT_IN_CHANNEL:
            await ctx.send("DB2 not in this channel.")
        case VC_STATE.SAME_SERVER_CHANNEL:
            server_data = data_manager.get_data(ctx)
            await server_data.vc_client.disconnect()
            server_data.vc_client = None
            server_data.song_queue = []