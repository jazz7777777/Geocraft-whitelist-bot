# Minecraft Whitelist & Moderation Bridge Bot

A Discord bot (discord.py 2.x) that bridges a Discord server to a **Paper**
Minecraft server running **Geyser/Floodgate**, automating:

1. **Reaction-based whitelisting** — staff react ✅ (Java) or 👍 (Bedrock) on a
   player's request message and the bot whitelists them via RCON.
2. **Slash commands** for moderators: `/whitelist add`, `/fwhitelist add`,
   `/ban`, `/tempban`.

---

## 1. Requirements

- Python 3.10+
- A Paper server with RCON enabled
- The [Floodgate](https://geysermc.org/) plugin installed (for `/fwhitelist`)
- A Discord application/bot with **Message Content** and **Server Members**
  privileged intents enabled (Discord Developer Portal → Bot → Privileged
  Gateway Intents)

## 2. Installation

```bash
git clone <this-project>
cd whitelist-bot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```env
DISCORD_TOKEN=your-bot-token-here
GUILD_ID=123456789012345678

WHITELIST_CHANNEL_ID=123456789012345678
WHITELISTED_ROLE_ID=1550918168103493632
MOD_ROLE_IDS=123456789012345678,987654321098765432

RCON_HOST=127.0.0.1
RCON_PORT=25575
RCON_PASSWORD=change-me

FLOODGATE_PREFIX=.
MIN_ACCOUNT_AGE_DAYS=7
```

- **GUILD_ID**: leave blank for global slash commands (can take up to an hour
  to appear); set it during development for instant sync.
- **MOD_ROLE_IDS**: comma-separated role IDs allowed to run moderator
  commands. Members with `Administrator` or `Manage Server` can always use
  them regardless of this list.
- **FLOODGATE_PREFIX**: must match the `username-prefix` set in Floodgate's
  `config.yml` (default is `.`).

## 3. Enable RCON on the Paper server

In `server.properties`:

```properties
enable-rcon=true
rcon.port=25575
rcon.password=change-me
broadcast-rcon-to-ops=false
```

Restart the server after changing this.

## 4. Run the bot

```bash
python bot.py
```

## 5. Invite the bot

Generate an invite URL in the Developer Portal with the `bot` and
`applications.commands` scopes, and at minimum these permissions:
`Send Messages`, `Embed Links`, `Read Message History`, `Add Reactions`,
`Manage Roles` (needed to grant the Whitelisted role — the bot's own role
must sit **above** that role in the role list).

---

## How reaction-based whitelisting works

Players post a message in the whitelist channel in this exact format:

```
Username: Notch
Version: Java
Device: PC
```

or for Bedrock:

```
Username: Steve123
Version: Bedrock / Pocket Edition
Device: iPhone 14
```

A moderator (or admin) then reacts:

| Reaction | Treated as | Console command run |
|---|---|---|
| ✅ | Java | `whitelist add <username>` |
| 👍 | Bedrock/PE | `fwhitelist add <prefix><username>` |

The bot recognizes `bedrock`, `pocket edition`, `pocket`, `pe`, and `geyser`
(case-insensitive, anywhere in the Version field) as Bedrock, and `java` as
Java.

### Validation performed before whitelisting

- **Non-moderator reactions are ignored** and the reaction is removed.
- **Already whitelisted** — if the message author already has the
  Whitelisted role, the bot posts a warning and does nothing else.
- **Malformed message** — missing/unparseable `Username:` or `Version:`
  fields produces an error embed with the expected format.
- **Invalid username** — Java names must be 3–16 alphanumeric/underscore
  characters; Bedrock gamertags must be ≤16 characters.
- **Reaction/version mismatch** — reacting ✅ on a request that says
  `Version: Bedrock` (or vice-versa) is rejected so no one gets whitelisted
  on the wrong pipeline by mistake.
- **New Discord accounts** — accounts younger than `MIN_ACCOUNT_AGE_DAYS`
  are flagged for manual review instead of being auto-whitelisted (basic
  anti-alt/anti-raid measure).
- **Server/RCON errors** — connection failures or a rejection from the
  server (e.g. "That player does not exist" for a bad/rate-limited Mojang
  lookup) are surfaced as a clear error embed instead of failing silently.

### On success

1. The player is added to the appropriate whitelist on the server.
2. The Whitelisted role (`WHITELISTED_ROLE_ID`) is granted to the requester.
3. A green success embed tags the player confirming they're ready to join.

---

## Slash commands (Moderator/Admin only)

| Command | Description | Console command executed |
|---|---|---|
| `/whitelist add <player>` | Whitelist a Java player | `whitelist add <player>` |
| `/fwhitelist add <player>` | Whitelist a Bedrock player | `fwhitelist add <prefix><player>` |
| `/ban <player> [reason]` | Ban a player | `ban <player> <reason>` |
| `/tempban <player> <duration> [reason]` | Temp-ban a player | `tempban <player> <duration> <reason>` |

- `duration` must match `\d+[smhdw]` (e.g. `30m`, `12h`, `1d`, `2w`).
- All commands validate that `player` looks like a plausible Minecraft
  username before touching the console.
- Anyone without Administrator/Manage Server permission or a role in
  `MOD_ROLE_IDS` gets a clean "no permission" ephemeral reply instead of the
  command silently failing.
- `/tempban` requires the [EssentialsX](https://essentialsx.net/) or
  equivalent plugin providing a `tempban` console command — swap the command
  string in `cogs/moderation.py` if your ban plugin uses different syntax.

---

## Project structure

```
whitelist-bot/
├── bot.py                    # Entry point, loads cogs, syncs slash commands
├── config.py                 # Env-var driven configuration
├── rcon_client.py            # Async RCON wrapper (mcrcon), raises RconError
├── requirements.txt
├── .env.example
├── utils/
│   ├── parser.py             # Username/Version/Device parsing + validation
│   └── checks.py             # Moderator permission check
└── cogs/
    ├── whitelist_listener.py # Reaction-based auto-whitelisting
    └── moderation.py         # /whitelist, /fwhitelist, /ban, /tempban
```

## Extending

- **Logging channel**: `LOG_CHANNEL_ID` is defined in config but not wired
  up yet — add a call in `_send_success`/`_send_error` to also post to that
  channel if you want an audit trail separate from the whitelist channel.
- **Different ban plugin**: if you're not using EssentialsX-style `ban`/
  `tempban`, edit the command strings built in `cogs/moderation.py`.
- **Custom emojis**: change `APPROVE_EMOJI`/`BEDROCK_EMOJI` in `config.py`
  if you'd rather use different reactions.
