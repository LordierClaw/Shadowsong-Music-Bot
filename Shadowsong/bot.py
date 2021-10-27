import discord
from discord.ext import commands

import configparser

config = configparser.ConfigParser()
config.read("config.ini")

BOT_TOKEN = config["HOST"]["BOT_TOKEN"]
PREFIX = config["BOT"]["Prefix"]

class ShadowsongBot(commands.Bot):
    def __init__(self):
        self._cogs = []
        if config["BOT"]["BasicCommand"] == "1":
            self._cogs.append("basic")
        if config["BOT"]["MusicBot"] == "1":
            self._cogs.append("music")
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