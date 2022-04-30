# This file is mainly to contain the code for a random dice roll.
from attr import has
import nextcord
import os
from nextcord.ext import commands
import youtube_dl


class Music(commands.Cog, name="Music"):
    """All commands related to music playback"""

    COG_EMOJI = "🎵"

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        """Joins the voice channel of the one who invoked the join command"""

        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()
    
    @commands.command()
    async def leave(self, ctx):
        """The bot will leave the channel it is in"""
        await ctx.voice_client.disconnect()
    

    @commands.command(aliases=['a'])
    async def add(self, ctx: commands.Context, arg):
        """ Adds the given youtube link to a queue to be played back


        Code checks for valid youtube link before adding it to the queue.
        Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ
        """
        await ctx.send("something")

    @commands.command()
    async def start(self, ctx, url : str):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(['https://www.youtube.com/watch?v=dQw4w9WgXcQ'])
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, "song.mp3")
        ctx.voice_client.play(nextcord.FFmpegPCMAudio("song.mp3"))



def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))