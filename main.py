import os

import discord
import dotenv
import json
from sreality import fresh_estates
from enum import Enum
from discord.ext import commands, tasks

Context = discord.ext.commands.context.Context

dotenv.load_dotenv()
DISCORD_TOKEN = os.getenv('BOT_TOKEN')


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

glob_config = {}
CONFIG_PATH = "config.json"


class ConfigKeys(Enum):
    DEFAULT_CHANNEL = "default_channel"


def load_config() -> dict:
    try:
        with open(CONFIG_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                return {}
    except FileNotFoundError:
        with open(CONFIG_PATH, 'w'):
            pass
        return {}


def save_config(config: dict) -> None:
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f)


@bot.event
async def on_ready():
    print(f"We are {bot.user.name}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)


@bot.command()
async def setchannel(ctx: Context, *args):
    global glob_config
    glob_config = load_config()

    channel_id = int(args[0][2:-1])
    channel = bot.get_channel(channel_id)

    if type(channel) != discord.channel.TextChannel:
        await ctx.send("Invalid channel.")

    glob_config[ConfigKeys.DEFAULT_CHANNEL.value] = channel_id
    save_config(glob_config)

    await ctx.send("Successfully registered channel.")


@tasks.loop(hours=1)
async def scrape_sreality():
    pass


bot.run(token=DISCORD_TOKEN)
