from typing import List
from discord.ext import commands
from discord import VoiceClient

class ServerData():
    def __init__(self):
        self.vc_client : VoiceClient = None
        self.song_queue : List[SongInfo] = []
        self.ai_context = []

class SongInfo():
    def __init__(self, source:str, title:str, duration:int, seek_sec:int=0):
        self.source = source
        self.title = title
        self.duration = duration
        self.seek_sec = seek_sec

server_datas = {}

def add_server_data(server_info:int|commands.Context):
    if type(server_info) == commands.Context:
        server_info = server_info.guild.id
    server_datas[server_info] = ServerData();
    return None


def get_data(server_info: int|commands.Context) -> ServerData:
    if type(server_info) == commands.Context:
        server_info = server_info.guild.id
    return server_datas[server_info]
