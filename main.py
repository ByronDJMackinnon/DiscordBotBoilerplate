"""This runs the bot, and opens an asyncio loop to have it running continuously."""
import os
from typing import Optional, Literal

import discord
from discord.ext import commands
import aiosqlite

from utils.config import TOKEN, CLIENT_ID

# Define intents
intents = discord.Intents.all()

# Create the bot instance
class CountryRP(commands.Bot):
    """This is the class that instantiates the bot."""
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, application_id=CLIENT_ID)
        self.db = None

    async def setup_hook(self):
        """This is called to setup anything the bot needs in order to operate"""
        # Load database
        self.db = await aiosqlite.connect("database.db")
        await self.init_db()
        # Load cogs during bot setup
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")

    async def init_db(self):
        """Initialize the database schema"""
        async with self.db.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                 discord_id INTEGER UNIQUE,
                                 username TEXT,
                                 joined_at TEXT
                                   )''')

    async def close(self):
        """Close the database connection when the bot stops"""
        if self.db:
            await self.db.close()

# Instantiate the bot
bot = CountryRP()

# Event: Bot is ready
@bot.event
async def on_ready():
    """Called whenever the bot is ready. This does get called repeatedly while the bot is online,\
        so keep that in mind when implementing anything within this function"""
    print(f"Bot is ready! Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_close():
    """When the bot closes, we close the connection to the websocket. This would be done automatically, \
        but in the event we need the bot to store some data we can put it in here."""
    await bot.close()

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
