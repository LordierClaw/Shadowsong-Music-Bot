import asyncio, re

import discord
from discord.errors import ClientException
from discord.ext import commands

from .util.Youtube import YoutubeExtractor
from .util.ServerQueue import Server, err

class Player:
    def __init__(self, server:Server, loop):
        self.server = server
        self._queue = server.Queue
        self.loop = loop

    def convert(self, url):
        ffmpeg_options = {
            'options': '-vn',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        }
        return discord.FFmpegPCMAudio(source=url, **ffmpeg_options)

    async def start(self, ctx):
        try:
            track = self._queue.now_playing
            audio = self.convert(YoutubeExtractor.get_audio(track.id))
            await asyncio.sleep(0.5)
            ctx.voice_client.play(
                audio,
                after=lambda e: asyncio.run_coroutine_threadsafe(self.moveAfter(ctx), loop=self.loop)
            )
            await ctx.send(f"**Now playing:** {track.title}")
        except err.NoMoreTracks:
            await ctx.send("There is nothing to play")
        except ClientException:
            #Already playing audio
            pass
    
    async def skip(self, ctx):
        try:
            await asyncio.sleep(0.5)
            ctx.voice_client.source.cleanup() #remove source to trigger moveAfter()
        except (err.NoMoreTracks, err.QueueIsEmpty):
            await ctx.send("There is nothing to play")
        except:
            await ctx.send("Error: player.skip()")
        
    async def moveAfter(self, ctx):
        if not self._queue.is_empty and not ctx.voice_client.is_playing():
            self._queue.remove(0)
            await self.start(ctx)

    async def stop(self, ctx):
        try:
            ctx.voice_client.stop()
        except:
            pass
    
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                try:
                    server = Server(before.channel.guild.id)
                    server.dispose()
                    await before.channel.guild.voice_client.disconnect()
                except:
                    pass

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
        server = Server(ctx.message.guild.id)
        try:
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            server.dispose()
            await ctx.send("Disconnected!")
        except AttributeError:
            await ctx.send("I'm not in any voice channel")
    
    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, args):
        server = Server(ctx.message.guild.id)
        is_new_queue = False
        if not server.is_registered():
            server.register()
            is_new_queue = True

        if ctx.author.voice:
            if ctx.voice_client is None:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.voice_client.move_to(ctx.author.voice.channel)
            addtrack = self.add(server, args)
            await ctx.send(addtrack)
            if is_new_queue == True:
                print("Getting audio ready")
                await Player(server, self.bot.loop).start(ctx)
                is_new_queue = False
        else:
            await ctx.send("You are not in any channel")
    
    def add(self, server:Server, args:str):
        URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        #Check URL_REGEX
        if not re.match(URL_REGEX, args):
            track = YoutubeExtractor.search_yt(args)
            server.Queue.add(track)
            return (f"**Added:** {track.title}")
        else:
            if "list=" in args:
                playlist = YoutubeExtractor.get_playlist(args)
                for track in playlist.items:
                    server.Queue.add(track)

                return (f"**Added** `{playlist.count}` videos from `{playlist.title}`")
            else:
                track = YoutubeExtractor.get_video(args)
                server.Queue.add(track)
                return (f"**Added:** {track.title}")

    @commands.command(name="skip", aliases=["s", "next"])
    async def skip(self, ctx):
        server = Server(ctx.message.guild.id)
        try:
            await Player(server, self.bot.loop).skip(ctx)
        except AttributeError:
            await ctx.send("There is nothing to skip")
    
    @commands.command(name="queue", aliases=["q", "list", "playlist"])
    async def queue(self, ctx):
        try:
            queue = Server(ctx.message.guild.id).Queue
            track = queue.now_playing
            if queue.length == 0:
                queue_str = "```ini\n[Queue is empty]```"
            else:
                queue_str = f"```ini\n[Now playing] {track.title}"
                if queue.length == 1:
                    queue_str = queue_str + "\n" + "\n[Queue is empty]```"

                elif queue.length <= 15:
                    for i in range(1, queue.length):
                        queue_str = queue_str + "\n" + (f"[{i}] {queue.get(i).title}")
                    queue_str = queue_str + "```"

                else:
                    for i in range(1, 16):
                        queue_str = queue_str + "\n" + (f"[{i}] {queue.get(i).title}")
                    queue_str = queue_str + "\n...and more```"
            await ctx.send(queue_str)
        except err.ServerNotRegistered:
            await ctx.send("```ini\n[Queue is empty]```")
    
    @commands.command(name="remove", aliases=["delete", "del", "rm"])
    async def remove(self, ctx, id):
        id = int(id)
        try:
            queue = Server(ctx.message.guild.id).Queue
            if id == 0:
                await ctx.send("```Invalid index.")
            else:
                try:
                    track_title = queue.get(id).title
                    queue.remove_in_queue(id)
                    await ctx.send(f"**Removed** {track_title} from queue")
                except err.TrackNotExist:
                    await ctx.send("```Invalid index.")
                except:
                    await ctx.send("```Error: Music.remove()")
        except err.ServerNotRegistered:
            await ctx.send("```ini\nThere is nothing to remove```")

    @commands.command(name="clear", aliases=["cl"])
    async def clear(self, ctx):
        server = Server(ctx.message.guild.id)
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        server.dispose()

def setup(bot):
    bot.add_cog(Music(bot))