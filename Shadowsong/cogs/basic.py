import os
from discord import Game as DiscordGame
from discord.ext import commands

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        version = os.getenv("VERSION")
        presence = f"$help | ver {version}"
        await self.bot.change_presence(activity=DiscordGame(name=presence))

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send(f"Current ping: {round(self.bot.latency * 1000)}ms")
    
    @commands.command(name="help")
    async def help(self, ctx):
        version = os.getenv("VERSION")
        author = os.getenv("AUTHOR")
        name = self.bot.user
        help_str = f"""```
[Name: {name}]
[Version: {version}]
[Author: {author}]
[Music Commands]
  $play or $p to stream audio from youtube
  $leave or $disconnect to disconnect the bot from channel
  $queue or $q to show the current queue/playlist
  $remove or $delete to remove a video from the queue (ex: $rm 2)
  $clear or $cl to clear the queue```"""
        await ctx.send(help_str)

def setup(bot):
    bot.remove_command("help")
    bot.add_cog(Basic(bot))