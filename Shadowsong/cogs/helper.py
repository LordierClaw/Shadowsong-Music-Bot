from discord import Game as DiscordGame
from discord.ext import commands

AUTHOR = "lordierclaw#4274"
VERSION = "0.7.2"

class Helper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        PREFIX = self.bot.getConfig()["prefix"]
        presence = f"{PREFIX}help | ver {VERSION}"
        await self.bot.change_presence(activity=DiscordGame(name=presence))

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send(f"Current ping: {round(self.bot.latency * 1000)}ms")
    
    @commands.command(name="help")
    async def help(self, ctx):
        PREFIX = self.bot.getConfig()["prefix"]
        help_str = f"""```
[Name: {self.bot.user}]
[Version: {VERSION}]
[Author: {AUTHOR}]"""
        music_help = f"""
[Music Commands]
  {PREFIX}play or {PREFIX}p to stream audio from youtube
  {PREFIX}leave or {PREFIX}disconnect to disconnect the bot from channel
  {PREFIX}queue or {PREFIX}q to show the current queue/playlist
  {PREFIX}remove or {PREFIX}delete to remove a video from the queue (ex: {PREFIX}rm 2)
  {PREFIX}skip or {PREFIX}next to skip the current track
  {PREFIX}loop or {PREFIX}repeat to start looping
  {PREFIX}clear or {PREFIX}cl to clear the queue```"""
        help_str = help_str + music_help
        await ctx.send(help_str)