# This file contains the code to modify nextcord (discord.py) built in help commands
# Code references from: https://gist.github.com/InterStella0/b78488fb28cadf279dfd3164b9f0cf96#brief

# We expect 3 kinds of input from the user
# !help (contains not argument we need to output all the cogs(groups of commands), and commands (found in each grouping of cogs)) -> send_bot_help
# !help Roll (contains a cog which is a group of commands (also the class name) will display all the commands under this group) -> send_cog_help
# !help roll (contains a command within a cog, display information only about the command)  -> send_command_help

from typing import Optional, Set
from nextcord.ext import commands
from nextcord import Embed

class MyHelpCommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        # clean_prefix is the prefix we need, qualified name is the command name, signature is how you call the command
        return f"{self.context.clean_prefix} {command.qualified_name} {command.signature}"

    # This helps us format the help message into an embeded object which looks nicer when the bot prints a message
    async def _help_embed(
        self, title: str, description: Optional[str] = None, mapping: Optional[dict] = None,
        command_set: Optional[Set[commands.Command]] = None):
        embed = Embed(title=title)
        if description:
            embed.description = description
        if command_set:
            # Show help about all commands in the set
            # Must filter out commands the invoker cannot see or use
            filtered = await self.filter_commands(command_set, sort=True)
            for command in filtered:
                # We use short_doc as that gives us the first line of the description rather than everything
                embed.add_field(
                    name=self.get_command_signature(command),
                    value=command.short_doc or "...",
                    inline=False)
        elif mapping:
            # add a short description of commands in each cog
            for cog, command_set in mapping.items():
                # Filter out the commands for the given user who issues the help command, not all users has access to every command.
                filtered = await self.filter_commands(command_set, sort=True)
                if not filtered:
                    continue
                name = cog.qualified_name if cog else "No category"
                # \u2002 is an en-space
                # Will give us a list of commands separated by a space that the use is allowed to use in the current cog
                cmd_list = "\u2002".join(
                    f"{self.context.clean_prefix}{cmd.name}" for cmd in filtered
                )
                # Here we combine the cog description and all the commands listed under it
                value = (
                    f"{cog.description}\n{cmd_list}"
                    if cog and cog.description
                    else cmd_list
                )
                # We add the cog to the embed and its coresponding commands.
                embed.add_field(name=name, value=value)
        return embed

    # This is the return statement when user types !help with not parameters (Thus we need to return all the commands and cogs)
    async def send_bot_help(self, mapping: dict):
        # Generate the embed for this call.
        embed = await self._help_embed(
            title="Bot Commands",
            description=self.context.bot.description,
            mapping = mapping
        )
        # Send the embed to where the user messaged for the help
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command: commands.Command):
        # Generate the embed for commands
        # command.help will check for the comments under the command
        embed = await self._help_embed(
            title=command.qualified_name,
            description=command.help,
            command_set=command.commands if isinstance(command, commands.Group) else None
        )
        await self.get_destination().send(embed=embed)
    
    async def send_cog_help(self, cog: commands.Command):
        # Go throught the cog and output all the commands within the set
        embed = await self._help_embed(
            title=cog.qualified_name,
            description=cog.description,
            command_set=cog.get_commands()
        )
        await self.get_destination().send(embed=embed)


class HelpCog(commands.Cog):
    """Shows help info about commands"""

    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self
        
    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot: commands.Bot):
    bot.add_cog(HelpCog(bot))