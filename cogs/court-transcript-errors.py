import discord
import datetime
import requests
import roblox
import sqlite3
import sys
import traceback

from discord.ext import commands
from discord.app_commands import AppCommandError
from roblox import InternalServerError

class CommandErrorHandler(commands.Cog, name="Command Error Handler"):

    def __init__(self, bot):
        self.bot = bot
    
    def cog_load(self):
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.on_app_command_error

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """
        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            if ctx.message.content.startswith('??') or ctx.message.content.startswith('!!'):
                return
            else:
                print('Unknown command sent')
                await ctx.send(':x: | I do not know that command. `!help` has a list of commands that can be used.', ephemeral=True)

        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.', ephemeral=True)
            
        elif isinstance(error, commands.NotOwner):
            await ctx.send(':x: | This command is restricted to the owner only.', ephemeral=True)
            
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(':x: | Argument needed', ephemeral=True)
            
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            await ctx.send(':x: | <@!222766150767869952> That cog is already loaded', ephemeral=True)
            
        elif isinstance(error, commands.ExtensionNotLoaded):
            await ctx.send(':x: | <@!222766150767869952> Could not load cog. Check the terminal for more details', ephemeral=True)
            
        elif isinstance(error, commands.ExtensionFailed):
            await ctx.send(':x: | <@!222766150767869952> Cog failed. Check the terminal for more details', ephemeral=True)
            
        elif isinstance(error, commands.ExtensionNotFound):
            await ctx.send(':x: | <@!222766150767869952> Could not find cog. Check the spelling and try again', ephemeral=True)
            
        elif isinstance(error, commands.CommandRegistrationError):
            await ctx.send(':x: | <@!222766150767869952> Command is already in service. Check the spelling and try again', ephemeral=True)
            
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f':x: | My perms got disabled. Please tag someone who can help! (Missing {error.missing_perms})', ephemeral=True)
            
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f':x: | You need the {error.missing_perms} permission to run this command!', ephemeral=True)
            
        elif isinstance(error, commands.MissingRole):
            await ctx.send(f'This command is restricted to {error.missing_role} only!', ephemeral=True)

        elif isinstance(error, commands.MissingAnyRole):
            await ctx.send(f':x: | This command can only be used by {error.missing_roles}', ephemeral=True)
            
        elif isinstance(error, ZeroDivisionError):
            await ctx.send('Cannot divide by zero!', ephemeral=True)
            
        elif isinstance(error, AttributeError):
            await ctx.send(f':x: | AttributeError: {error}', ephemeral=True)
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            channel = ctx.bot.get_channel(784368117299150849)
            embed = discord.Embed(
                type='rich',
                colour = discord.Colour.red()
            )
            embed.set_author(name='New Error', icon_url=str(ctx.bot.user.avatar))
            embed.add_field(name='Attribute Error', value=f'{error}', inline=False)
            embed.add_field(name='Command Ran', value=f'{ctx.command}', inline=False)
            embed.add_field(name='Guild', value=f'{ctx.guild}', inline=True)
            embed.add_field(name='Channel', value=f'{ctx.channel}', inline=True)
            embed.add_field(name='Message', value=f'{ctx.message.content}', inline=True)
            embed.set_footer(text=f'User ID: {ctx.author.id}', icon_url=str(ctx.author.avatar))
            embed.timestamp = datetime.datetime.now()
            await channel.send(embed=embed)
            
        elif isinstance(error, NameError):
            await ctx.send(f':x: | NameError: {error}', ephemeral=True)
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        
        elif isinstance(error, ValueError):
            await ctx.send(f':x: | ValueError: {error}', ephemeral=True)
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        
        elif isinstance(error, SyntaxError):
            await ctx.send(f':x: | SyntaxError: {error}', ephemeral=True)
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            
        elif isinstance(error, KeyError):
            await ctx.send(f':x: | KeyError: {error} is not found', ephemeral=True)
            
        elif isinstance(error, TypeError):
            await ctx.send(f':x: | TypeError: {error}', ephemeral=True)
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        
        elif isinstance(error, IndexError):
            await ctx.send(f':x: | IndexError: {error}', ephemeral=True)
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            
        elif isinstance(error, discord.HTTPException):
            if error.status == 403 and error.code == 50013 and ctx.command.qualified_name == 'ban' or ctx.command.qualified_name == 'kick':
                prefix = await self.bot.get_prefix(ctx.message)
                await ctx.send(f'{ctx.author.mention} Yeah no, I ain\'t doing {prefix}{ctx.command.qualified_name} on {ctx.message.mentions[0].mention}.', ephemeral=True)
            else:
                await ctx.send(f':x: | HTTPException: {error.status} (error code: {error.code}): {error.text}', ephemeral=True)
        
#         if isinstance(error, requests.RequestsException):
#             await ctx.send(':x: | There was an ambiguous exception that occurred while trying to fetch the API data.')
#             
#         if isinstance(error, requests.ConnectionError):
#             await ctx.send(':x: | Could not connect to the API.')
#             
#         if isinstance(error, requests.HTTPError):
#             await ctx.send(':x: | An HTTP error occurred.')
#         
#         if isinstance(error, requests.URLRequired):
#             await ctx.send(':x: | Uhhhh, <@222766150767869952> you deleted the URL...')
#             
#         if isinstance(error, requests.TooManyRedirects):
#             await ctx.send(':x: | API has too many redirects.')
#             
#         if isinstance(error, requests.ConnectTimeout):
#             await ctx.send(':x: | The request timed out while trying to connect to the API.')
#             
#         if isinstance(error, requests.ReadTimeout):
#             await ctx.send(':x: | API didn\'t respond in time. Please try again.')
#         
#         if isinstance(error, requests.Timeout):
#             await ctx.send(':x: | The request timed out. Please try again.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.BadArgument):
            await ctx.send(error, ephemeral=True)
            
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(':x: | Error not captured')
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            channel = ctx.bot.get_channel(784368117299150849)
            embed = discord.Embed(
                type='rich',
                colour = discord.Colour.red()
            )
            embed.set_author(name='New Error', icon_url=str(ctx.bot.user.avatar))
            embed.add_field(name='Check Failure Error', value=f'{error}', inline=False)
            embed.add_field(name='Command Ran', value=f'{ctx.command}', inline=False)
            embed.add_field(name='Guild', value=f'{ctx.guild}', inline=True)
            embed.add_field(name='Channel', value=f'{ctx.channel}', inline=True)
            embed.add_field(name='Message', value=f'{ctx.message.content}', inline=True)
            embed.set_footer(text=f'User ID: {ctx.author.id}', icon_url=str(ctx.author.avatar))
            embed.timestamp = datetime.datetime.now()
            await channel.send(embed=embed)

        elif isinstance(error, commands.UserInputError):
            if ctx.command.qualified_name == 'transcript':
                await ctx.send(error, ephemeral=True)
            else:
                await ctx.send(':x: | UserInputError: {}'.format(error), ephemeral=True)
                print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
                traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

        elif isinstance(error, commands.CheckAnyFailure):
            await ctx.send("Error not captured. Sent to console for capturing", ephemeral=True)
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            channel = ctx.bot.get_channel(784368117299150849)
            embed = discord.Embed(
                type='rich',
                colour = discord.Colour.red()
            )
            embed.set_author(name='New Error', icon_url=str(ctx.bot.user.avatar))
            embed.add_field(name='Check Any Failure Error', value=f'{error}', inline=False)
            embed.add_field(name='Command Ran', value=f'{ctx.command}', inline=False)
            embed.add_field(name='Guild', value=f'{ctx.guild}', inline=True)
            embed.add_field(name='Channel', value=f'{ctx.channel}', inline=True)
            embed.add_field(name='Message', value=f'{ctx.message.content}', inline=True)
            embed.set_footer(text=f'User ID: {ctx.author.id}', icon_url=str(ctx.author.avatar))
            embed.timestamp = datetime.datetime.now()
            await channel.send(embed=embed)

        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    async def on_app_command_error(self, interaction:discord.Interaction, error:AppCommandError):
        print('Ignoring exception in command {}:'.format(interaction.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(name='repeat', aliases=['mimic', 'copy'], hidden=True)
    async def do_repeat(self, ctx, *, inp: str):
        """A simple command which repeats your input!
        Parameters
        ------------
        inp: str
            The input you wish to repeat.
        """
        await ctx.send(inp)

    @do_repeat.error
    async def do_repeat_handler(self, ctx, error):
        """A local Error Handler for our command do_repeat.
        This will only listen for errors in do_repeat.
        The global on_command_error will still be invoked after.
        """

        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'inp':
                await ctx.send("You forgot to give me input to repeat!")


async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))