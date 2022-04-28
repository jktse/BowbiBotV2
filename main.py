import os
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv

# Load the Bot Token, this is important as it tells Discord API who we are
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Intents are used to determine what the bot is allowed to do
intents = nextcord.Intents.default()
# bot is going to be the main callback that will await commands or instructions
bot = commands.Bot(command_prefix='!', intents=intents)

# Path to the file remember that use dot to replace slashes and if there are none it automatically assumes .py
for folder in os.listdir("modules"):
    if os.path.exists(os.path.join("modules", folder, "cog.py")):
        bot.load_extension(f"modules.{folder}.cog")

class Application():
    # This tells the bot to boot up
    bot.run(BOT_TOKEN)
    
def main():
    app = Application()

if __name__ == '__main__':
    main()