import discord
from discord.ext import commands

from utils import Database

class EventCog(commands.Cog):
    """Cog to contain all of the events for organizational purposes. """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Called once the cog is ready. This is called repeatedly while the bot is active."""
        print(f"{self.__class__.__name__} loaded and ready.")

# Setup function for the cog
async def setup(bot):
    await bot.add_cog(EventCog(bot))