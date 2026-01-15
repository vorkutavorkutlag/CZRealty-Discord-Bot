import os

import discord
import dotenv

dotenv.load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')


class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}')


intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)


if __name__ == "__main__":
    client.run(BOT_TOKEN)
