# This file is mainly to contain the code for a random dice roll.
from attr import has
import nextcord
from nextcord.ext import commands
import youtube_dl

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


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
    

    @commands.command(aliases=['a'])
    async def add(self, ctx: commands.Context, arg):
        """ Adds the given youtube link to a queue to be played back

        Code checks for valid youtube link before adding it to the queue.
        Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ
        """
        await ctx.send("something")


def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))