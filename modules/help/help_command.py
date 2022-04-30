# This file contains the code to modify nextcord (discord.py) built in help commands
# Code references from: https://gist.github.com/InterStella0/b78488fb28cadf279dfd3164b9f0cf96
# We expect 3 kinds of input from the user
# !help (contains not argument we need to output all the cogs(groups of commands), and commands (found in each grouping of cogs)) -> send_bot_help
# !help Roll (contains a cog which is a group of commands (also the class name) will display all the commands under this group) -> send_cog_help
# !help roll (contains a command within a cog, display information only about the command)  -> send_command_help
# If the user submits a regular !help command we add some interactivivity, I might consider adding it to cogs to help filter the commands as well.

from multiprocessing.sharedctypes import Value
from typing import Optional, Set
from nextcord.ext import commands
from nextcord import Embed
import nextcord

class HelpDropdown(nextcord.ui.Select):
    # When we initialize for the help dropdown, might get replaced for pagination
    def __init__(self, help_command: "MyHelpCommand", options: list[nextcord.SelectOption]):
        super().__init__(placeholder="Choose a category...", min_values=1, max_values=1, options=options)
        self._help_command = help_command

    # We wait for interaction made on the dropdown, if there is an interaction we update the help message for the user
    # We update the embed information, self.values[0] is part of the drop down and we have the cog's label set at values[0]
    # If there is no change nothing changes otherwise we get all the commands maped to the cog
    async def callback(self, interaction: nextcord.Interaction):
        embed = (
            await self._help_command.cog_help_embed(self._help_command.context.bot.get_cog(self.values[0]))
            if self.values[0] != self.options[0].value
            else await self._help_command.bot_help_embed(self._help_command.get_bot_mapping())
        )
        await interaction.response.edit_message(embed=embed)

class HelpView(nextcord.ui.View):
    # This is used to generate the dropdown that we see. We pass in the information about our help command
    # The list of options the downdown will have as well as the timeout for the view
    def __init__(self, help_command: "MyHelpCommand", options: list[nextcord.SelectOption], *, timeout: Optional[float] = 120.0):
        super().__init__(timeout=timeout)
        self.add_item(HelpDropdown(help_command, options))
        self._help_command = help_command

    # When the timeout has been reached for the help dropdown it will terminate kill everything. Thus the need to rewrite the last known help
    async def on_timeout(self) -> None:
        self.clear_items()
        await self._help_command.response.edit(view=self)
    
    # This is meant to verify the one who invoked the help call is the one who can play with the dropdown
    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return self._help_command.context.author == interaction.user




class MyHelpCommand(commands.MinimalHelpCommand):
    # Returns how the command should be formated in a string
    def get_command_signature(self, command):
        return f"{self.context.clean_prefix} {command.qualified_name} {command.signature}"

    # Returns the list of cogs which the user can see (Commands are filtered based on the user's permision)
    async def _cog_select_option(self) -> list[nextcord.SelectOption]:
        options: list[nextcord.SelectOption] = []
        options.append(nextcord.SelectOption(
            label="Home",
            emoji="🏠",
            description="Go back to homepage"
        ))

        for cog, command_set in self.get_bot_mapping().items():
            filtered = await self.filter_commands(command_set, sort=True)
            if not filtered:
                continue
            emoji = getattr(cog, "COG_EMOJI", None)
            # Note description for SelectOption cannot be longer than 100 characters
            options.append(nextcord.SelectOption(
                label = cog.qualified_name if cog else "No Category",
                emoji=emoji,
                description = cog.description[:100] if cog and cog.description else None,
                ))
        return options

    # Returns an Embed object that will contain all the information we want to display
    # Embeds contains 2 main parts the Title (instantiated at the beginning) and a fields (The body of the embed)
    # We break the field adding into 2 parts set of commands vs. mapping
    # If we are calling from the COG and want the set of commands then command_set is true
    # If we are calling from the home (!help) then we need all the cogs called a mapping.
    # In both cases we need pull the command information out however the level of detail is different
    async def _help_embed(
        self, title: str, description: Optional[str] = None, mapping: Optional[dict] = None,
        command_set: Optional[Set[commands.Command]] = None
        ) -> Embed:
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
                emoji = getattr(cog, "COG_EMOJI", None)
                cog_label = f"{emoji} {name}" if emoji else name
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
                embed.add_field(name=cog_label, value=value)
        return embed

    # This is called when !help is called, this returns an Embed object created from _help_embed
    async def bot_help_embed(self, mapping: dict) -> Embed:
        return await self._help_embed(
            title="Bot Commands",
            description=self.context.bot.description,
            mapping = mapping
        )

    # This is called when ever the user invoke !help with not arguments. Therefore we generate the dropdown
    async def send_bot_help(self, mapping: dict):
        # Generate the embed for this call.
        embed = await self.bot_help_embed(mapping)
        # Get the list of Cogs the users can see (options in terms of things seen on the dropdown)
        options = await self._cog_select_option()
        # Send the embed to where the user messaged for the help
        self.response = await self.get_destination().send(embed=embed, view=HelpView(self, options))

    # This is called when the user invokes !help [command]. We print the description of the command.
    async def send_command_help(self, command: commands.Command):
        # Generate the embed for commands
        # command.help will check for the comments under the command
        emoji = getattr(command.cog, "COG_EMOJI", None)
        embed = await self._help_embed(
            title=f"{emoji} {command.qualified_name}" if emoji else command.qualified_name,
            description=command.help,
            command_set=command.commands if isinstance(command, commands.Group) else None
        )
        await self.get_destination().send(embed=embed)

    # This returns the cogs information interms of an embed, we also add in the emoji to the top as a title
    async def cog_help_embed(self, cog: commands.Cog) -> Embed:
        emoji = getattr(cog, "COG_EMOJI", None)
        return await self._help_embed(
            title=f"{emoji} {cog.qualified_name}" if emoji else cog.qualified_name,
            description=cog.description,
            command_set=cog.get_commands()
        )
    
    # This is called when the user invoke !help [COG]. We output all the cog commands to the user.
    async def send_cog_help(self, cog: commands.Command):
        embed = await self.cog_help_embed(cog)
        await self.get_destination().send(embed=embed)