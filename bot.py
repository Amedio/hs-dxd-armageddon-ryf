import discord
import random
import utils
import ryf
import asyncio
import configparser
import os
from discord.ext import commands
from discord import Embed

bot_token = os.environ['BOT_TOKEN']

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.run(bot_token)
