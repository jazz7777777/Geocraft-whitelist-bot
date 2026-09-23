"""
Entry point for the Minecraft whitelist/moderation bridge bot.

Run with:  python bot.py
Requires a filled-in .env (copy from .env.example).
"""
import asyncio
import logging

import discord
from discord.ext import commands

from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("bot")

INTENTS = discord.Intents.default()
INTENTS.message_content = True  # needed to read "Username:/Version:/Device:" text
INTENTS.members = True          # needed to check/assign the Whitelisted role

EXTENSIONS = (
    "cogs.whitelist_listener",
    "cogs.moderation",
)


class WhitelistBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=INTENTS, help_command=None)

    async def setup_hook(self) -> None:
        for extension in EXTENSIONS:
            await self.load_extension(extension)
            log.info("Loaded extension: %s", extension)

        if Config.GUILD_ID:
            # Guild-scoped sync is near-instant; great for development.
            guild = discord.Object(id=Config.GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
        else:
            # Global sync can take up to an hour to propagate.
            synced = await self.tree.sync()
        log.info("Synced %d application command(s)", len(synced))

    async def on_ready(self) -> None:
        log.info("Logged in as %s (ID: %s)", self.user, self.user.id if self.user else "?")


async def main() -> None:
    if not Config.DISCORD_TOKEN:
        raise SystemExit("DISCORD_TOKEN is not set. Copy .env.example to .env and fill it in.")
    if not Config.RCON_PASSWORD:
        log.warning("RCON_PASSWORD is empty — server console commands will fail until it's set.")
    if not Config.WHITELIST_CHANNEL_ID:
        log.warning("WHITELIST_CHANNEL_ID is not set — reaction-based whitelisting is disabled.")

    bot = WhitelistBot()
    async with bot:
        await bot.start(Config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
