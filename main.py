import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import domain.data_manager as data_manager
from helpers import check_vc_command, VC_STATE

intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True
client = commands.Bot(command_prefix='!', intents=intents)

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f'cogs.{filename[:-3]}')

@client.event
async def on_command_error(ctx,error):
    if not isinstance(error, discord.ext.commands.CommandNotFound):
        return
    await ctx.send(embed=discord.Embed(title="Invalid command.",color=discord.Color.red()))

@client.event
async def on_ready():
    print("#### DB2 Ready ####")
    print("Adding server data entries ... ", end="")
    for guild in client.guilds:
        data_manager.add_server_data(guild.id)
    print("Complete")


@client.command()
async def join(ctx:commands.Context):
    match check_vc_command(ctx):
        case VC_STATE.USER_NOT_IN_VC:
            await ctx.send("Join VC for VC command.")
        case VC_STATE.BOT_NOT_IN_SERVER:
            new_vc_client = await ctx.message.author.voice.channel.connect()
            data_manager.get_data(ctx).vc_client = new_vc_client
            print("Joind vc, session ID: " + new_vc_client.session_id)
        case VC_STATE.BOT_NOT_IN_CHANNEL:
            await data_manager.get_data(ctx).vc_client.move_to(ctx.author.voice.channel)

@client.command()
async def dc(ctx:commands.Context):
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
    

async def main():
    await load_cogs()
    await client.start(DISCORD_TOKEN)

asyncio.run(main())