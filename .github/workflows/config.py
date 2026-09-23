"""
Central configuration for the whitelist/moderation bridge bot.
All values are loaded from environment variables (see .env.example).
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _get_int(env_key: str, default: str = "0") -> int:
    raw = os.getenv(env_key, default).strip()
    return int(raw) if raw.isdigit() else int(default)


def _get_int_list(env_key: str) -> list[int]:
    raw = os.getenv(env_key, "")
    return [int(part.strip()) for part in raw.split(",") if part.strip().isdigit()]


class Config:
    # --- Discord ---
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
    GUILD_ID = _get_int("GUILD_ID", "0") or None  # set for instant guild-scoped command sync

    WHITELIST_CHANNEL_ID = _get_int("WHITELIST_CHANNEL_ID", "0")
    LOG_CHANNEL_ID = _get_int("LOG_CHANNEL_ID", "0") or None
    WHITELISTED_ROLE_ID = _get_int("WHITELISTED_ROLE_ID", "1550918168103493632")
    MOD_ROLE_IDS = _get_int_list("MOD_ROLE_IDS")

    # --- Minecraft server (RCON) ---
    RCON_HOST = os.getenv("RCON_HOST", "127.0.0.1")
    RCON_PORT = _get_int("RCON_PORT", "25575")
    RCON_PASSWORD = os.getenv("RCON_PASSWORD", "")

    # --- Floodgate / Geyser ---
    FLOODGATE_PREFIX = os.getenv("FLOODGATE_PREFIX", ".")

    # --- Anti-alt safety net ---
    MIN_ACCOUNT_AGE_DAYS = _get_int("MIN_ACCOUNT_AGE_DAYS", "7")

    # --- Reaction emojis ---
    APPROVE_EMOJI = "✅"   # Java
    BEDROCK_EMOJI = "👍"   # Bedrock / Pocket Edition
