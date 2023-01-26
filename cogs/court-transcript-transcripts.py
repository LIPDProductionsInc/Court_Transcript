import discord
import chat_exporter
import io
import json

from discord import app_commands
from discord.ext import commands

class TranscriptCog(commands.Cog, name="Transcript Commands"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.hybrid_command(name='transcript', description='Get a transcript of the case')
    @commands.guild_only()
    async def transcript(self, ctx: commands.Context) -> None:
        if discord.utils.get(ctx.author.roles, id=322925337887637505) or discord.utils.get(ctx.author.roles, id=322925757435346944) or discord.utils.get(ctx.author.roles, id=322925014280306700):
            with open('dockets.json', 'r') as f:
                dockets = json.load(f)
            if ctx.channel.name in dockets:
                await ctx.send("`Saving...`")
                try:
                    channel = ctx.bot.get_channel(626911454322491422)
                    transcript = await chat_exporter.export(ctx.channel, tz_info='EST')
                    transcript_file = discord.File(io.BytesIO(transcript.encode()),filename=f"{ctx.channel.name}.html")
                    await ctx.send(file=transcript_file)
                    await channel.send(ctx.channel.name, file=transcript_file)
                except Exception as e:
                    await ctx.send(f"`{e}`", ephemeral=True)
                    print("Ignoring exception in command transcript: {}".format(e))
            else:
                raise commands.UserInputError("This command can only be used in a case channel.")
        else:
            raise commands.UserInputError("You do not have permission to use this command.")
            pass
        pass

    pass

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TranscriptCog(bot))