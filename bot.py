import discord
import random
import utils
import ryf
import asyncio
import configparser
import os
import psycopg2
import database
from discord.ext import commands
from discord import Embed

bot_token = os.environ['BOT_TOKEN']

bot = commands.Bot(command_prefix='d!')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def roll(ctx, bonus:int=0, difficulty:int=0, dice:str='n'):
    dice_index = 1
    if dice == 'down' or dice == 'd':
        dice_index = 0
    elif dice == 'up' or dice == 'u':
        dice_index = 2
    
    roll_result = ryf.attr_skill_roll(dice_index)

    all_rolls = roll_result[0]
    total_roll = roll_result[1]
    critical_failure_next = 0
    if len(roll_result) == 3:
        critical_failure_next = roll_result[2]

    if total_roll == 1:
        rich=Embed(title="El resultado de la tirada de {0.author.display_name} es **PIFIA**".format(ctx), color=0xffffff)
        rich.add_field(name="tirada", value=all_rolls, inline=False)
        rich.add_field(name="dado objetivo", value=total_roll, inline=True)
        if critical_failure_next > 0:
            rich.add_field(name="dado siguiente", value=critical_failure_next, inline=True)

        await ctx.send(embed=rich)
        return

    total = total_roll + bonus

    rich=Embed(title="El resultado de la tirada de {0.author.display_name} es **{1}**".format(ctx, total), color=0xffffff)
    rich.add_field(name="tirada", value=all_rolls, inline=True)
    rich.add_field(name="dado objetivo", value=total_roll, inline=True)
    
    if bonus > 0 or difficulty > 0:
        rich.add_field(name="total", value="{0} + {1} = {2}".format(total_roll, bonus, total), inline=False)

        if difficulty > 0:
            if total >= difficulty:
                rich.add_field(name="resultado", value="ÉXITO", inline=True)
            else:
                rich.add_field(name="resultado", value="FALLO", inline=True)
            if total - difficulty >= 10:
                rich.add_field(name="crítico", value="CRÍTICO", inline=True)

    await ctx.send(embed=rich)

@bot.command()
async def effect(ctx, dice_amount:int, bonus:int=0):
    if dice_amount >= 100:
        async with ctx.typing():
            await asyncio.sleep(3)
            await ctx.send("https://media.giphy.com/media/9JjnmOwXxOmLC/giphy.gif")
            return

    roll_result = ryf.effect_roll(dice_amount)
    
    all_rolls = roll_result[0]
    total_roll = roll_result[1]

    total = total_roll + bonus

    rich=Embed(title="El resultado de la tirada de {0.author.display_name} es **{1}**".format(ctx, total), color=0xffffff)
    rich.add_field(name="tirada", value=all_rolls, inline=True)
    rich.add_field(name="total", value=total_roll, inline=True)
    if bonus > 0:
        rich.add_field(name="total", value="{0} + {1} = {2}".format(total_roll, bonus, total), inline=False)

    await ctx.send(embed=rich)

@bot.command()
async def char(ctx, shortcut:str, name:str, thumbnail:str):
    if database.exists_char(shortcut):
        database.update_char(shortcut, name, thumbnail)
    else:
        is_master = ctx.author.id == 474238638708883476
        if is_master or not database.player_has_char(ctx.author.name):
            database.insert_char(shortcut, name, thumbnail, ctx.author.name)
        else:
            await ctx.send('No eres el masta y ya tienes un personaje')

@bot.command()
async def say(ctx, text:str, shortcut:str=''):
    if ctx.message.channel.category_id != 487701272309268484:
        await ctx.send("Estás en un canal que no pertenece a ON-ROL")
        return

    rich=Embed(title=text, color=0xffffff)

    if shortcut != '':
        row = database.select_char_shortcut(shortcut)
    else:
        row = database.select_char_player(ctx.author.name)

    rich.set_author(name=row[2])
    rich.set_thumbnail(url=row[3])

    await ctx.message.delete()

    await ctx.send(embed=rich)

@bot.command()
async def combat(ctx):
    await ctx.send(ctx.message.channel.id)

bot.run(bot_token)
