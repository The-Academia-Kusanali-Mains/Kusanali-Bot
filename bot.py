import discord
from discord.ext import commands

from os import listdir
from os.path import isfile, join

import asyncio
from aiohttp import ClientSession
from datetime import datetime
from core.logger import get_logger
import uvloop

from core.database import database
from core.settings import Settings

logger = get_logger(__name__)


class KusanaliBot(commands.Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.settings = Settings(self)
        self.settings.load_cache()

        self.session = None
        self.api = database(self)
        self.db = self.api.db
        self.connected = asyncio.Event()

        self.start_time = datetime.utcnow()
        self.on_start()

    def on_start(self):
        for cog in [file.replace('.py', '') for file in listdir("cogs") if isfile(join('cogs', file))]:
            logger.info(f"Loading cog: {cog}")

            try:
                self.load_extension('cogs' + '.' + cog)
                logger.info(f"Successfully loaded {cog}")
            except Exception:
                logger.error(f"Failed to log {cog}")

    def get_session(self):
        if self.session is None:
            self.session = ClientSession(loop=self.loop)
        return self.session

    async def run(self):
        await self.start(self.settings["bot_token"])

    async def on_connect(self):
        self.api.validate_connection

        await self.settings.load()
        self.connected.set()

    async def on_ready(self):
        await self.wait_until_ready()
        await self.connected.wait()
        await self.settings.ready
        # add a bunch of logger stuff telling bot info


if __name__ == '__main__':
    bot = KusanaliBot()
    bot.run()