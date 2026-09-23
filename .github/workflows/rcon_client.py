"""
Thin async wrapper around the synchronous `mcrcon` library so RCON calls
never block the bot's event loop, and so failures surface as a single
predictable exception type the cogs can catch and turn into embeds.
"""
import asyncio
import logging

from mcrcon import MCRcon, MCRconException

from config import Config

log = logging.getLogger("rcon")


class RconError(Exception):
    """Raised whenever a console command could not be executed or confirmed."""


async def send_command(command: str) -> str:
    """
    Run a single command against the Minecraft server console over RCON.
    Returns the raw text response from the server. Raises RconError on any
    connection, auth, or protocol failure.
    """
    command = command.strip()
    if not command:
        raise RconError("Refusing to send an empty console command.")

    def _run_blocking() -> str:
        try:
            with MCRcon(Config.RCON_HOST, Config.RCON_PASSWORD, port=Config.RCON_PORT, timeout=10) as mcr:
                return mcr.command(command)
        except MCRconException as exc:
            raise RconError(f"RCON authentication/protocol error: {exc}") from exc
        except (ConnectionRefusedError, TimeoutError, OSError) as exc:
            raise RconError(
                f"Could not reach the server console at {Config.RCON_HOST}:{Config.RCON_PORT} ({exc})."
            ) from exc

    try:
        result = await asyncio.to_thread(_run_blocking)
        log.info("RCON `%s` -> %r", command, result)
        return result
    except RconError:
        raise
    except Exception as exc:  # pragma: no cover - defensive catch-all
        log.exception("Unexpected failure running RCON command %r", command)
        raise RconError(f"Unexpected error while contacting the server: {exc}") from exc
