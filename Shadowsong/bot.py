from discord.ext import commands

from termcolor import colored
import colorama
colorama.init()

import json
config = json.load(open("config.json"))

BOT_TOKEN = config["token"]
PREFIX = config["prefix"]
BOT_NAME = "Shadowsong"

class DiscordBot(commands.Bot):
    def __init__(self):
        self._cogs = []
        if config["settings"]["helper"] == 1:
            self._cogs.append("helper")
        if config["settings"]["basic"] == 1:
            self._cogs.append("basic")
        
        from discord import Intents
        intents = Intents.all()
        super().__init__(command_prefix=self.prefix, case_insensitive=True, intents=intents)

    async def setup(self):
        print(colored(f"[{BOT_NAME}]", "blue"), "Running setup...")
        from .cogs.helper import Helper
        from .cogs.music import Music
        self.remove_command('help')
        for cog in self._cogs:
            if cog == "helper":
                await self.add_cog(Helper(self))
            elif cog == "basic":
                await self.add_cog(Music(self))
            print(colored(f"[{BOT_NAME}]", "blue"),"Loaded", colored(f"[{cog}]", "yellow"), "cog.")

        print(colored(f"[{BOT_NAME}]", "blue"), colored("Setup completed.", "green"))

    def run(self):
        import asyncio
        asyncio.run(self.setup())
        print(colored(f"[{BOT_NAME}]", "blue"), "Running bot...")
        super().run(BOT_TOKEN, reconnect=True)
        super().remove_command("help")

    async def shutdown(self):
        print(colored(f"[{BOT_NAME}]", "blue"), colored("Closing connection to Discord...", "red"))
        await super().close()

    async def close(self):
        print(colored(f"[{BOT_NAME}]", "blue"), colored("Closing on keyboard interrupt...", "red"))
        await self.shutdown()

    async def on_connect(self):
        if round(self.latency * 1000) <= 100:
            ping_color = "green"
        elif round(self.latency * 1000) <= 250:
            ping_color = "yellow"
        else:
            ping_color = "red"
        print(colored(f"[{BOT_NAME}]", "blue"), colored(f"Connected to Discord", "green"), "| latency:", colored(f"{round(self.latency * 1000)}ms", ping_color))

    async def on_resumed(self):
        print(colored(f"[{BOT_NAME}]", "blue"), colored("Bot resumed.", "green"))

    async def on_disconnect(self):
        print(colored(f"[{BOT_NAME}]", "blue"), colored("Bot disconnected.", "red"))

    async def on_error(self, err, *args, **kwargs):
        raise

    async def on_command_error(self, ctx, exc):
        raise getattr(exc, "original", exc)

    async def on_ready(self):
        print(colored(f"[{BOT_NAME}]", "blue"), "Logged in as", colored("{0}".format(self.user), "cyan"))
        print('------------------------------------------------------')
        print(colored(f"[{BOT_NAME}]", "blue"), colored("Everything is ready.", "cyan"))

    async def prefix(self, bot, msg):
        return commands.when_mentioned_or(PREFIX)(bot, msg)

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        if ctx.command is not None:
            await self.invoke(ctx)

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)

    def getConfig(self):
        return config