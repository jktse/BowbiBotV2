# This file is mainly to contain the code for a random dice roll.
from nextcord.ext import commands

class Roll(commands.Cog, name="Roll"):
    """Recieves roll commands"""

    COG_EMOJI = "🎲"

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx: commands.Context):
        """ Rolls a given amount of dice in the form \_d\_

        Example: !roll 2d6
        This is asking for 2 dice rolls of a 6 sided dice
        """
        await ctx.send("something")

    @commands.command()
    async def choose(self, ctx: commands.Context, *args):       # *args for an unlimited number of inputs, all put into an array
        """ Chooses a random item from the given input, if the item is mutiple words used " "

        Example: !choose First Second "Third Option"
        One of the above inputs will be choosen, "Third Option will be designated as one word
        """
        await ctx.send("something")


def setup(bot: commands.Bot):
    bot.add_cog(Roll(bot))