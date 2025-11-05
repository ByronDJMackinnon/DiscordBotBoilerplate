"""This runs the bot, and opens an asyncio loop to have it running continuously."""
#* Standard Imports
import os
import asyncio
import logging
from typing import Optional, Literal
from dotenv import load_dotenv

#* 3rd Party Imports
import discord
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncEngine

#* Custom Imports
from utils.database import Base, Database
from cogs import get_cog_names

import logging

#? Configure the logger globally
logger = logging.getLogger("discord_bot")
logger.setLevel(logging.DEBUG)

#? Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

#? Formatter
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')
ch.setFormatter(formatter)

#? Add handler to logger
logger.addHandler(ch)

#? Define intents
intents = discord.Intents.all()

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")

# Create the bot instance
class TestBot(commands.Bot):
    """This is the class that instantiates the bot."""
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, application_id=CLIENT_ID)
        self.logger = logger
        self.db: Database | None = None

    async def setup_hook(self):
        """This is called to setup anything the bot needs in order to operate"""
        # 1) Initialize Database & keep it on the bot object
        self.db = Database(DATABASE_URL, echo=False)
        await self.db.connect()

        #! This is DEV only. In production I must use Alembic instead of create_all
        async with self.db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Load cogs during bot setup
        for cog in get_cog_names():
            await self.load_extension(cog)

    async def close(self):
        # graceful shutdown
        if self.db:
            await self.db.disconnect()
        await super().close()

# Instantiate the bot
bot = TestBot()

# Event: Bot is ready
@bot.event
async def on_ready():
    """Called whenever the bot is ready. This does get called repeatedly while the bot is online,\
        so keep that in mind when implementing anything within this function"""
    print(f"Bot is ready! Logged in as {bot.user} (ID: {bot.user.id})")

    # activity = discord.Activity(type=discord.ActivityType.playing, name="some pick-up games!")
    # await bot.change_presence(activity=activity)

@bot.event
async def on_close():
    """When the bot closes, we close the connection to the websocket. This would be done automatically, \
        but in the event we need the bot to store some data we can put it in here."""
    await bot.close()

@bot.event
async def on_command_error(ctx, error):
    """Handles all prefix command errors."""
    if isinstance(error, commands.CommandNotFound):
        return

    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the required permissions.")

    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Try again in {round(error.retry_after, 2)} seconds.")

    else:
        await ctx.send("An unexpected error occurred.")
        print(f"[Prefix Command Error] {error}")

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """Handles all slash command errors."""
    if isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have the required permissions.", ephemeral=True)

    elif isinstance(error, discord.app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"Cooldown! Try again in {round(error.retry_after, 2)} seconds.", ephemeral=True)

    else:
        if interaction.response.is_done():
            await interaction.followup.send("An unexpected error occurred.", ephemeral=True)
        else:
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)
        print(f"[Slash Command Error] {error}")

@bot.tree.command(name="load", description="Load a cog")
@commands.is_owner()
async def load_cog(interaction: discord.Interaction, cog: str):
    try:
        await bot.load_extension(f"cogs.{cog}")
        await interaction.response.send_message(f"✅ Loaded `{cog}` successfully.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to load `{cog}`: {e}")

@bot.tree.command(name="unload", description="Unload a cog")
@commands.is_owner()
async def unload_cog(interaction: discord.Interaction, cog: str):
    try:
        await bot.unload_extension(f"cogs.{cog}")
        await interaction.response.send_message(f"✅ Unloaded `{cog}` successfully.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to unload `{cog}`: {e}")

@bot.tree.command(name="reload", description="Reload a cog")
@commands.is_owner()
async def reload_cog(interaction: discord.Interaction, cog: str):
    try:
        await bot.reload_extension(f"cogs.{cog}")
        await interaction.response.send_message(f"✅ Reloaded `{cog}` successfully.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to reload `{cog}`: {e}")

@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec:Optional[Literal["~", "*", "^"]] = None) -> None:
    """Syncs app_commands to the development guild"""
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}")

bot.run(TOKEN)
