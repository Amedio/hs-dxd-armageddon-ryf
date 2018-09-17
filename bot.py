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

bot = commands.Bot(command_prefix='d!')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(description='Escribe d!roll [down|d|up|u] [nivel_habilidad [dificultad]]')
async def roll(ctx, *args):
    bonus = 0
    difficulty = 0
    dice_index = 1

    if len(args) == 1 and utils.is_int(args[0]):
        bonus = int(args[0])
    elif len(args) == 2 and utils.is_int(args[0]) and utils.is_int(args[1]):
        bonus = int(args[0])
        difficulty = int(args[1])
    elif len(args) == 3 and utils.is_int(args[1]) and utils.is_int(args[2]):
        bonus = int(args[1])
        difficulty = int(args[2])
    elif len(args) == 2 and utils.is_int(args[1]):
        bonus = int(args[1])

    dice_index = 1
    if len(args) > 0 and not utils.is_int(args[0]):
        if args[0] == 'down' or args[0] == 'd':
            dice_index = 0
        elif args[0] == 'up' or args[0] == 'u':
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

@bot.command(description='Escribe d!effect numero_dados [bonus]')
async def effect(ctx, arg1, arg2=0):
    bonus = arg2
    dice_amount = int(arg1)
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
async def say(ctx, arg1, arg2):
    pc = arg1
    text = arg2

    await ctx.send(":scream: :{0}: **{1}**".format(pc, text))

bot.run(bot_token)
