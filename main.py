import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load the Bot Token, this is important as it tells Discord API who we are
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Intents are used to determine what the bot is allowed to do
intents = discord.Intents.default()
# bot is going to be the main callback that will await commands or instructions
bot = commands.Bot(command_prefix='!', intents=intents)

bot.load_extension("help") # Path to the file, instead of using a slash use a period

class Application():
    # This tells the application to boot up
    bot.run(BOT_TOKEN)
    

def main():
    app = Application()

if __name__ == '__main__':
    main()