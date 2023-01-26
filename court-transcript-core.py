import discord
import asyncio
import os
import logging

from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

class MyBot(commands.Bot):
    async def setup_hook(self):
        for extension in initial_extensions:
            await self.load_extension(extension)
    
def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    # Notice how you can use spaces in prefixes. Try to keep them simple though.
    prefixes = ['!', '?']

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)

bot = MyBot(command_prefix=get_prefix, help_command=None, case_insensitive=True, intents=discord.Intents.all(), fetch_offline_users=True, allowed_mentions=discord.AllowedMentions(everyone=True, roles=True, users=True))
tree = bot.tree

initial_extensions = ['cogs.court-transcript-admin',
                      'cogs.court-transcript-errors',
                      'cogs.court-transcript-owner',
                      'cogs.court-transcript-transcripts'
                    ]

@bot.event
async def on_ready():
    print(f'Successfully logged in as {bot.user}, Running Verison 0.0.0.1'.format(bot))
    activity = discord.Activity(name='the court | !help', type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)
    await asyncio.sleep(1)
    bot.owner = bot.get_user(222766150767869952)
    await tree.sync()
    print('Slash commands synced!')
    await asyncio.sleep(2)
    print('Running discord.py version ' + discord.__version__)
    await asyncio.sleep(2)
    print('Cogs loaded:')
    await asyncio.sleep(1)
    print(bot.cogs)

@bot.event
async def on_user_update(before, after):
    try:
        if after.id == bot.owner.id and before.name != after.name:
            bot.owner = bot.get_user(bot.owner.id)
    except AttributeError:
        pass

async def main():
    await bot.setup_hook()
    await bot.start(os.getenv('TOKEN'))

asyncio.run(main())
