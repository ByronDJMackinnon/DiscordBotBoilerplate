"""Test Commands for organizational purposes."""

import discord
from discord.ext import commands
from discord import app_commands

class TestCog(commands.Cog):
    """Cog to contain all of the Test commands for organizational purposes. """
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Responds with Pong!")
    async def ping(self, interaction: discord.Interaction):
        """Boilerplate command."""
        await interaction.response.send_message("Pong!")

    @commands.Cog.listener()
    async def on_ready(self):
        """Called once the cog is ready. This is called repeatedly while the bot is active."""
        print(f"{self.__class__.__name__} loaded and ready.")

# Setup function for the cog
async def setup(bot):
    await bot.add_cog(TestCog(bot))
