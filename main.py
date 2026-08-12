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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")


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

    if not scrape_sreality.is_running():
        scrape_sreality.start()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)


@bot.command()
async def setchannel(ctx: Context, channel: discord.TextChannel):
    global glob_config
    glob_config = load_config()
    glob_config[ConfigKeys.DEFAULT_CHANNEL.value] = channel.id
    save_config(glob_config)
    await ctx.send(f"Successfully registered {channel.mention}.")



@tasks.loop(hours=1)
async def scrape_sreality():
    await bot.wait_until_ready()

    channel_id = load_config()[ConfigKeys.DEFAULT_CHANNEL.value]
    channel: discord.TextChannel = bot.get_channel(channel_id)

    estates = fresh_estates()
    if not estates:
        # print("Nothing new under the sun.")
        return

    for estate_url in estates:
        embed = discord.Embed(title="New estate found!", url=estate_url, description=estate_url)
        await channel.send(embed=embed)


@bot.command()
async def force_sreality(_ctx, *_args):
    await scrape_sreality()


bot.run(token=DISCORD_TOKEN)
