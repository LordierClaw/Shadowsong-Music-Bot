from discord import Game as DiscordGame
from discord.ext import commands

import configparser

config = configparser.ConfigParser()
config.read("config.ini")

AUTHOR = config["INFO"]["Author"]
VERSION = config["INFO"]["Version"]
PREFIX = config["BOT"]["Prefix"]

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        presence = f"{PREFIX}help | ver {VERSION}"
        await self.bot.change_presence(activity=DiscordGame(name=presence))

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send(f"Current ping: {round(self.bot.latency * 1000)}ms")
    
    @commands.command(name="help")
    async def help(self, ctx):
        help_str = f"""```
[Name: {self.bot.user}]
[Version: {VERSION}]
[Author: {AUTHOR}]"""
        if config["BOT"]["MusicBot"] == "1":
            music_help = f"""
[Music Commands]
  {PREFIX}play or {PREFIX}p to stream audio from youtube
  {PREFIX}leave or {PREFIX}disconnect to disconnect the bot from channel
  {PREFIX}queue or {PREFIX}q to show the current queue/playlist
  {PREFIX}remove or {PREFIX}delete to remove a video from the queue (ex: {PREFIX}rm 2)
  {PREFIX}skip or {PREFIX}next to skip the current track
  {PREFIX}clear or {PREFIX}cl to clear the queue```"""
            help_str = help_str + music_help
        else:
            help_str = help_str + "```"
        await ctx.send(help_str)

def setup(bot):
    bot.remove_command("help")
    bot.add_cog(Basic(bot))