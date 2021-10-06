import discord
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="connect", aliases=["join"])
    async def join(self, ctx):
        if ctx.author.voice:
            if ctx.voice_client is None:
                await ctx.author.voice.channel.connect()
                await ctx.send("Connected!")
            else:
                await ctx.voice_client.move_to(ctx.author.voice.channel)
                await ctx.send("I'm already in voice channel")
        else:
            await ctx.send("You haven't connected to a voice channel.")

    @commands.command(name="disconnect", aliases=["leave"])
    async def leave(self, ctx):
        server_id = ctx.message.guild.id
        try:
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected!")
        except AttributeError:
            await ctx.send("I'm not in any voice channel")

def setup(bot):
    bot.add_cog(Music(bot))