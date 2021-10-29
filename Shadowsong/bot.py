import discord
from discord.ext import commands

import configparser

config = configparser.ConfigParser()
config.read("config.ini")

BOT_TOKEN = config["HOST"]["BOT_TOKEN"]
PREFIX = config["BOT"]["Prefix"]

from termcolor import colored
import colorama
colorama.init()

class ShadowsongBot(commands.Bot):
    def __init__(self):
        self._cogs = []
        if config["BOT"]["BasicCommand"] == "1":
            self._cogs.append("basic")
        if config["BOT"]["MusicBot"] == "1":
            self._cogs.append("music")
        super().__init__(command_prefix=self.prefix, case_insensitive=True)

    def setup(self):
        print(colored("[Shadowsong]", "blue"), "Running setup...")

        for cog in self._cogs:
            self.load_extension(f"Shadowsong.cogs.{cog}")
            print(colored(f"[Shadowsong]", "blue"),"Loaded", colored(f"[{cog}]", "yellow"), "cog.")

        print(colored("[Shadowsong]", "blue"), colored("Setup completed.", "green"))

    def run(self):
        self.setup()
        print(colored("[Shadowsong]", "blue"), "Running bot...")
        super().run(BOT_TOKEN, reconnect=True)
        super().remove_command("help")

    async def shutdown(self):
        print(colored("[Shadowsong]", "blue"), colored("Closing connection to Discord...", "red"))
        await super().close()

    async def close(self):
        print(colored("[Shadowsong]", "blue"), colored("Closing on keyboard interrupt...", "red"))
        await self.shutdown()

    async def on_connect(self):
        if round(self.latency * 1000) <= 100:
            ping_color = "green"
        elif round(self.latency * 1000) <= 250:
            ping_color = "yellow"
        else:
            ping_color = "red"
        print(colored("[Shadowsong]", "blue"), colored(f"Connected to Discord", "green"), "| latency:", colored(f"{round(self.latency * 1000)}ms", ping_color))

    async def on_resumed(self):
        print(colored("[Shadowsong]", "blue"), colored("Bot resumed.", "green"))

    async def on_disconnect(self):
        print(colored("[Shadowsong]", "blue"), colored("Bot disconnected.", "red"))

    async def on_error(self, err, *args, **kwargs):
        raise

    async def on_command_error(self, ctx, exc):
        raise getattr(exc, "original", exc)

    async def on_ready(self):
        print(colored("[Shadowsong]", "blue"), "Logged in as", colored("{0}".format(self.user), "cyan"))
        print('------------------------------------------------------')
        print(colored("[Shadowsong]", "blue"), colored("Everything is ready.", "cyan"))

    async def prefix(self, bot, msg):
        return commands.when_mentioned_or(PREFIX)(bot, msg)

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        if ctx.command is not None:
            await self.invoke(ctx)

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)