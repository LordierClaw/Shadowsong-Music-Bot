from pathlib import Path
import os

import discord
from discord.ext import commands

BOT_TOKEN = os.getenv("BOT_TOKEN")
PREFIX = "$"

class MusicBot(commands.Bot):
    def __init__(self):
        self._cogs = [p.stem for p in Path(".").glob("./Shadowsong/cogs/*.py")]
        super().__init__(command_prefix=self.prefix, case_insensitive=True)

    def setup(self):
        print("[Shadowsong] Running setup...")

        for cog in self._cogs:
            self.load_extension(f"Shadowsong.cogs.{cog}")
            print(f"[Shadowsong] Loaded [{cog}] cog.")

        print("[Shadowsong] Setup complete.")

    def run(self):
        self.setup()
        print("[Shadowsong] Running bot...")
        super().run(BOT_TOKEN, reconnect=True)
        super().remove_command("help")

    async def shutdown(self):
        print("[Shadowsong] Closing connection to Discord...")
        await super().close()

    async def close(self):
        print("[Shadowsong] Closing on keyboard interrupt...")
        await self.shutdown()

    async def on_connect(self):
        print(f"[Shadowsong] Connected to Discord | latency: {round(self.latency * 1000)}ms.")

    async def on_resumed(self):
        print("[Shadowsong] Bot resumed.")

    async def on_disconnect(self):
        print("[Shadowsong] Bot disconnected.")

    async def on_error(self, err, *args, **kwargs):
        raise

    async def on_command_error(self, ctx, exc):
        raise getattr(exc, "original", exc)

    async def on_ready(self):
        print('[Shadowsong] Logged in as {0}'.format(self.user))
        print('------------------------------------------------------')
        await self.change_presence(activity=discord.Game(name="$help | ver 0.0.1"))
        print('Everything is ready.')

    async def prefix(self, bot, msg):
        return commands.when_mentioned_or(PREFIX)(bot, msg)

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        if ctx.command is not None:
            await self.invoke(ctx)

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)