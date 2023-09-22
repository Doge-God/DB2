import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import domain.data_manager as data_manager
from common import check_vc_command, VC_STATE, join_voice_chan, disconnect_voice_chan

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
    await join_voice_chan(ctx)

@client.command()
async def dc(ctx:commands.Context):
    await disconnect_voice_chan(ctx)
    
async def main():
    async with client:
        await load_cogs()
        await client.start(DISCORD_TOKEN)

asyncio.run(main())