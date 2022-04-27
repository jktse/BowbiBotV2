import os
import discord
from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

client = discord.Client()
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print("Tesr")

class Application():
    client.run(BOT_TOKEN)
    

def main():
    app = Application()

if __name__ == '__main__':
    main()