import discord
import aiohttp
import asyncio
import datetime
import json
import psutil
import sys
import traceback

from discord.ext import commands

class OwnerCog(commands.Cog, name="Owner Commands"):

    def __init__(self, bot):
        self.bot = bot
    
    # Hidden means it won't show up on the default help.
    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def _load(self, ctx, *, cog: str):
        await ctx.send(f'**`Loading Cog: {cog}...`**')
        """Command which Loads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            print('Loading cog...')
            await asyncio.sleep(0.1)
            print('Cog name:')
            await asyncio.sleep(0.1)
            print(cog)
            await asyncio.sleep(2)
            await self.bot.load_extension(f'cogs.court-transcript-{cog}')
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            print('Ignoring exception in loading cog {}:'.format(cog), file=sys.stderr)
            traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        else:
            await ctx.send(f'**`Cog: {cog} has loaded successfully`**')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def _unload(self, ctx, *, cog: str):
        await ctx.send(f'**`Unloading Cog: {cog}...`**')
        await asyncio.sleep(2)
        """Command which Unloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            print('Unloading cog...')
            await asyncio.sleep(0.1)
            print('Cog name:')
            await asyncio.sleep(0.1)
            print(cog)
            await self.bot.unload_extension(f'cogs.court-transcript-{cog}')
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            print('Ignoring exception in unloading cog {}:'.format(cog), file=sys.stderr)
            traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        else:
            print(f'{cog} has unloaded successfully!')
            await ctx.send(f'**`Successfuly unloaded Cog: {cog}`**')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""
        print('Reloading cog...')
        await asyncio.sleep(0.1)
        print('Cog Name:')
        await asyncio.sleep(0.1)
        print(cog)
        try:
            await ctx.send(f'**`Unloading Cog: {cog}...`**')
            await self.bot.unload_extension(f'cogs.court-transcript-{cog}')
            await asyncio.sleep(2)
            await ctx.send(f'**`Loading Cog: {cog}...`**')
            await self.bot.load_extension(f'cogs.court-transcript-{cog}')
            await asyncio.sleep(1)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            print('Ignoring exception in reloading cog {}:'.format(cog), file=sys.stderr)
            traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        else:
            await ctx.send(f'**`Successfully loaded {cog}`**')
            print(f'Cog: {cog} has loaded sucessfuly!')
            pass
        pass

    @commands.command(name='sync', hidden=True)
    @commands.is_owner()
    async def _sync(self, ctx) -> None:
        await ctx.send('`Syncing Slash commands...`')
        print('Syncing slash commands')
        synced = await ctx.bot.tree.sync()
        await ctx.send(f"`Synced {len(synced)} commands`")
        print(f"Synced {len(synced)} commands")
        return

    
    @commands.command(name='eval', hidden=True)
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')
                pass
            pass
        pass
    
    @commands.command(name='edit', hidden=True)
    @commands.is_owner()
    async def _edit(self, ctx, id, content):
        message = await ctx.fetch_message(id)
        await message.edit(content=content)
        pass

    @commands.command(name='edit-specific', hidden=True)
    @commands.is_owner()
    async def _edit_specific(self, ctx, type = None):
        if type == None:
            await ctx.send('Please specify a type', ephemeral=True)
        else:
            raise commands.BadArgument('Invalid type specified')
            pass
    
    @commands.command(name='stats', hidden=True)
    @commands.is_owner()
    async def _stats(self, ctx):
        embed = discord.Embed(
            title='Court Transcript',
            type='rich',
            colour=discord.Color.dark_blue(),
            description=f'''
Python Version: **{sys.version}**

Discord.py Version: **{discord.__version__}**

Current CPU Usage: **{psutil.cpu_percent()}**%

Current RAM Usage: **{psutil.virtual_memory().percent}**%

Average System Load: **{[x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]}%**

Latency: **{round(self.bot.latency * 1000)}**ms
'''
            )
        embed.set_footer(text=f"Developed by {self.bot.owner}")
        embed.set_thumbnail(url=str(self.bot.user.avatar))
        await ctx.send(embed=embed)
        pass

    @commands.command(name='restart', hidden=True)
    @commands.is_owner()
    async def _restart(self, ctx):
        await ctx.send('Restarting...')
        await self.bot.logout()
        pass

    @commands.hybrid_command(name='test', hidden=True)
    @commands.is_owner()
    async def _test(self, ctx):
        print("This test command is used for quick debugging of code and to understand what the bot sees based on the code written.")
        await ctx.send('Sent')
        pass

    pass

async def setup(bot):
    await bot.add_cog(OwnerCog(bot))
