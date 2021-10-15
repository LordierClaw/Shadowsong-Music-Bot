import asyncio, re

import discord
from discord.ext import commands

from .util.Youtube import YoutubeExtractor
from .util.ServerQueue import ServerQueue

from .util.ServerQueue import Video as Video
from .util.Youtube import Playlist as Playlist

NoneType = type(None)

class Player(discord.PCMVolumeTransformer):
    def __init__(self, source, *, volume=0.7):
        super().__init__(source, volume)
    
    ffmpeg_options = {
        'options': '-vn',
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
    } 

    @classmethod
    def stream(self, url):
        return discord.FFmpegPCMAudio(executable='C:/FFmpeg/bin/ffmpeg.exe', source=url, **self.ffmpeg_options)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await before.channel.guild.voice_client.disconnect()

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
            await ctx.send("You haven't connected to a voice channel")

    @commands.command(name="disconnect", aliases=["leave"])
    async def leave(self, ctx):
        try:
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected!")
        except AttributeError:
            await ctx.send("I'm not in any voice channel")
    
    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, url):
        queue = ServerQueue(ctx.message.guild.id)
        queue.register()

        if ctx.author.voice:
            if ctx.voice_client is None:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.voice_client.move_to(ctx.author.voice.channel)
            asyncio.run_coroutine_threadsafe(self.add(ctx, url), loop=self.bot.loop)
        else:
            await ctx.send("You are not in any channel")
    
    async def add(self, ctx, url):
        queue = ServerQueue(ctx.message.guild.id)

        URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        #Check URL_REGEX
        if not re.match(URL_REGEX, url):
            video = YoutubeExtractor.search_yt(url)
            queue.add_to_queue(video)

            if ctx.voice_client.is_connected():
                await ctx.send(f"**Added:** {video.title}")
        else:
            if "list=" in url:
                playlist = YoutubeExtractor.get_playlist(url)
                for video in playlist.items:
                    queue.add_to_queue(video)

                await ctx.send(f"**Added** `{playlist.count}` videos from `{playlist.title}`")
            else:
                video = YoutubeExtractor.get_video(url)
                queue.add_to_queue(video)

        asyncio.run_coroutine_threadsafe(self.startQueue(ctx), loop=self.bot.loop)

    async def startQueue(self, ctx):
        queue = ServerQueue(ctx.message.guild.id)
        
        def move_to_next_song():
            try:
                ctx.voice_client.stop()
            except AttributeError:
                pass
            finally:
                queue.remove_in_queue(0)
                asyncio.run_coroutine_threadsafe(self.startQueue(ctx), loop=self.bot.loop)
        
        if not ctx.voice_client.is_playing() and queue.get_length() == 0:
            await ctx.send("There is nothing else to play")
            queue.dispose()
        elif not ctx.voice_client.is_playing() and queue.get_length() != 0:
            vid = queue.get_current_playing()
            audio = YoutubeExtractor.get_audio(vid.id)
            player = Player.stream(audio)
            ctx.voice_client.play(player, after=lambda e: move_to_next_song())
            await ctx.send(f"**Now playing:** {vid.title}")

    @commands.command(name="skip", aliases=["s", "next"])
    async def skip(self, ctx):
        queue = ServerQueue(ctx.message.guild.id)
        
        try:
            if ctx.voice_client.is_playing() and (queue.get_length() == 0 or queue.get_queue() is None):
                ctx.voice_client.stop()
                queue.dispose()
            elif not ctx.voice_client.is_playing() and (queue.get_length() == 0 or queue.get_queue() is None):
                await ctx.send("There is nothing else to skip")
            else:
                ctx.voice_client.stop()
                asyncio.run_coroutine_threadsafe(self.startQueue(ctx), loop=self.bot.loop)
        except AttributeError:
            await ctx.send("There is nothing to skip")
    
    @commands.command(name="queue", aliases=["q", "list", "playlist"])
    async def queue(self, ctx):
        queue = ServerQueue(ctx.message.guild.id)

        vid = queue.get_current_playing()

        queue_str = f"```ini\n[Now playing] {vid.title}"
        queue_length = queue.get_length()
        if queue_length == 0:
            if vid is NoneType:
                queue_str = "```ini\n[Queue is empty]```"
            else:
                queue_str = queue_str + "\n" + "\n[Queue is empty]```"

        elif queue_length <= 15:
            for i in range(1, queue_length):
                queue_str = queue_str + "\n" + (f"[{i}] {queue.get_item(i).title}")
            queue_str = queue_str + "```"

        else:
            for i in range(1, 16):
                queue_str = queue_str + "\n" + (f"[{i}] {queue.get_item(i).title}")
            queue_str = queue_str + "\n...and more```"
        await ctx.send(queue_str)
    
    @commands.command(name="remove", aliases=["delete", "del", "rm"])
    async def remove(self, ctx, id):
        queue = ServerQueue(ctx.message.guild.id)

        try:
            vid_title = queue.get_item(int(id)).title
            queue.remove_in_queue(int(id))
            await ctx.send(f"**Remove** {vid_title} from queue")
        except IndexError:
            await ctx.send("Invalid index.")
        except:
            await ctx.send("An error occurred.")

    @commands.command(name="clear", aliases=["cl"])
    async def clear(ctx):
        queue = ServerQueue(ctx.message.guild.id)
        queue.dispose()
        queue.register()

def setup(bot):
    bot.add_cog(Music(bot))