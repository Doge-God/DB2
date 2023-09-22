
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