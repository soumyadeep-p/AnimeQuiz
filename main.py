
import discord
from discord.ext import commands as coms
import json
import commands
import song_player


with open('config.json') as f:
    json_data = json.load(f)
    PREFIX = json_data['PREFIX']
    TOKEN = json_data['TOKEN']

bot = coms.Bot(command_prefix=PREFIX, intents=discord.Intents.all())


# Load commands cog
async def load_commands():
    print("Loading all commands..")
    await bot.load_extension("commands")
    await bot.load_extension("song_player")
    print("Finished loading all commands.")


@bot.event
async def on_ready():
    print("Bot is now online.")
    await load_commands()


if __name__ == '__main__':
    print("Loading Bot..")
    bot.run(TOKEN)
