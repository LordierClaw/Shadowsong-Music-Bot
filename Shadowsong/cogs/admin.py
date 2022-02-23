import os
import discord
from discord.ext import commands

from .util.ServerQueue import Server
from music import Player

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name="admin")
    async def admin(self, ctx, *, member: discord.Member=None):
        if ctx.invoked_subcommand is None:
            await ctx.send("No command was given")
        if member.id != 220181441944879104 or member.id != 220181441944879104:
            await ctx.send("You are not the admin, please contact lordierclaw#4274")
    
    @admin.command(name="get-all")
    async def getAll(self, ctx):
        if Server.getDatabase() == {}:
            await ctx.send("```Database is empty```")
        else:
            for item in Server.getDatabase():
                server_id, is_loop, queue_length, loopqueue_length = item
                context = f"```ini\n[{server_id}]\nis_loop={is_loop}\nqueue_len={queue_length}\nloop_queue_len={loopqueue_length}```"
                await ctx.send(context)
    
    @admin.command(name="get-queue")
    async def getQueue(self, ctx, args=None):
        if args != None:
            content = Player(Server(int(args), None)).getQueue()
            content = content.removeprefix("```ini").removesuffix("```").strip()
            filename = f"{ctx.message.guild.id}-queue.ini"
            with open(filename, "w", encoding="UTF-8") as file:
                file.write(content)
            with open(filename, "rb") as file:
                await ctx.send(file=discord.File(file, filename))
            os.remove(filename)
        else:
            await ctx.send("```No guild id was given```")
    
    @admin.command(name="force-dispose")
    async def forceDispose(self, ctx, args=None):
        if args != None:
            Server(int(args)).dispose()
            await ctx.send(f"{args} is disposed")
        else:
            await ctx.send("```No guild id was given```")

    @admin.command(name="force-register")
    async def forceRegister(self, ctx, args=None):
        if args != None:
            Server(int(args)).register()
            await ctx.send(f"{args} is registered")
        else:
            await ctx.send("```No guild id was given```")
    
    @admin.command(name="send-msg")
    async def sendMsg(self, ctx, id, *, msg:str):
        channel = self.bot.get_channel(int(id))
        await channel.send(msg)
        await ctx.send(f"```Message Sent to {id}:\n{msg}")
        
def setup(bot):
    bot.add_cog()