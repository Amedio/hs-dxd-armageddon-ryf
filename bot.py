import discord
import random
import utils
import asyncio
import configparser
import os
import psycopg2
from validator_collection import checkers
from discord.ext import commands
from discord import Embed
from discord import Client
from database import characterdao
from database import channelroledao
from database import memberroledao
from dxd import DxD

bot_token = os.environ['BOT_TOKEN']

bot = commands.Bot(command_prefix='d!')

rules = DxD()

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def roll(ctx, skill_bonus:int=0, skill_difficulty:int=0, e_dice_amount:int=0, e_bonus:int=0, skill_dice:str='n'):
    dice_index = 1
    if skill_dice == 'down' or skill_dice == 'd':
        dice_index = 0
    elif skill_dice == 'up' or skill_dice == 'u':
        dice_index = 2
    
    roll_result = rules.attr_skill_roll(dice_index)

    all_rolls = roll_result[0]
    total_roll = roll_result[1]
    critical_failure_next = 0
    if len(roll_result) == 3:
        critical_failure_next = roll_result[2]

    if total_roll == 1:
        rich = Embed(title="El resultado de la tirada de {0.author.display_name} es **PIFIA**".format(ctx), color=0xffffff)
        rich.add_field(name="tirada", value=all_rolls, inline=False)
        rich.add_field(name="dado objetivo", value=total_roll, inline=True)
        if critical_failure_next > 0:
            rich.add_field(name="dado siguiente", value=critical_failure_next, inline=True)

        await ctx.send(embed=rich)
        return

    total = total_roll + skill_bonus

    rich=Embed(title="El resultado de la tirada de {0.author.display_name} es **{1}**".format(ctx, total), color=0xffffff)
    rich.add_field(name="tirada", value=all_rolls, inline=True)
    rich.add_field(name="dado objetivo", value=total_roll, inline=True)
    
    if skill_bonus > 0 or skill_difficulty > 0:
        rich.add_field(name="total", value="{0} + {1} = {2}".format(total_roll, skill_bonus, total), inline=False)

        if skill_difficulty > 0:
            if total >= skill_difficulty:
                rich.add_field(name="resultado", value="ÉXITO", inline=True)
            else:
                rich.add_field(name="resultado", value="FALLO", inline=True)
            if total - skill_difficulty >= 10:
                if e_dice_amount > 0:
                    critical_times = (total - skill_difficulty) // 10
                    e_dice_amount = e_dice_amount + critical_times
                    rich.add_field(name="crítico", value="CRÍTICO " + str(critical_times) + " veces", inline=True)
                else:
                    rich.add_field(name="crítico", value="CRÍTICO", inline=True)

    await ctx.send(embed=rich)

    if total >= skill_difficulty and e_dice_amount > 0:
        await effect_call(ctx, e_dice_amount, e_bonus)

@bot.command()
async def effect(ctx, dice_amount:int, bonus:int=0):
    await effect_call(ctx, dice_amount, bonus)

async def effect_call(ctx, dice_amount:int, bonus:int=0):
    if dice_amount >= 100:
        async with ctx.typing():
            await asyncio.sleep(3)
            await ctx.send("https://media.giphy.com/media/9JjnmOwXxOmLC/giphy.gif")
            return

    roll_result = rules.effect_roll(dice_amount)
    
    all_rolls = roll_result[0]
    total_roll = roll_result[1]

    total = total_roll + bonus

    rich = Embed(title="El resultado de la tirada de {0.author.display_name} es **{1}**".format(ctx, total), color=0xffffff)
    rich.add_field(name="tirada", value=all_rolls, inline=True)
    rich.add_field(name="total", value=total_roll, inline=True)
    if bonus > 0:
        rich.add_field(name="total", value="{0} + {1} = {2}".format(total_roll, bonus, total), inline=False)

    await ctx.send(embed=rich)

@bot.command()
async def char_dev(ctx):
    await ctx.message.delete()
    
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel

    starting_creation = await ctx.send("{0.author.display_name} comienza la creación de un personaje".format(ctx))
    query_shortcut = await ctx.send("Escribe un atajo para referirte a tu personaje:")
    response_shortcut = await bot.wait_for('message', check=pred)
    shortcut = response_shortcut.content

    await delete_messages(query_shortcut, response_shortcut)

    if characterdao.exists_shortcut_guild(shortcut, ctx.guild.id):
        character = characterdao.get_shortcut_guild(shortcut, ctx.guild.id)

        shortcut = character.shortcut
        name = character.name
        thumbnail = character.thumbnail

        rich = Embed(title="El personaje tendrá el atajo: {0}".format(shortcut), color=0xffffff)
        rich.set_author(name=name)
        rich.set_thumbnail(url=thumbnail)

        char_preview = await ctx.send(embed=rich)
        query_wichpartedit = await ctx.send("Elige el número del atributo que quieres cambiar:\n1. Nombre\n2. Avatar\n3. Guardar\n4. Cancelar")
        response_whichpartedit = await bot.wait_for('message', check=pred)
        whichpartedit = response_whichpartedit.content

        await delete_messages(char_preview, query_wichpartedit, response_whichpartedit)

        while whichpartedit != '4' and whichpartedit != '3':
            if whichpartedit == '2':
                query_thumbnail = await ctx.send("Escribe la url del avatar de tu personaje:")
                response_thumbnail = await bot.wait_for('message', check=pred)
                thumbnail = response_thumbnail.content
                await query_thumbnail.delete()
                await response_thumbnail.delete()
                await starting_creation.delete()

                if not checkers.is_url(thumbnail):
                    error_message = await ctx.send('El valor **{0}** para *thumbnail* no es una URL'.format(thumbnail))
                    await asyncio.sleep(10)
                    await error_message.delete()
                    return
            elif whichpartedit == '1':
                query_name = await ctx.send("Escribe el nombre de tu personaje:")
                response_name = await bot.wait_for('message', check=pred)
                name = response_name.content
                await query_name.delete()
                await response_name.delete()

            rich = Embed(title="El personaje tendrá el atajo: {0}".format(shortcut), color=0xffffff)
            rich.set_author(name=name)
            rich.set_thumbnail(url=thumbnail)

            char_preview = await ctx.send(embed=rich)
            query_wichpartedit = await ctx.send("Elige el número del atributo que quieres cambiar:\n1. Nombre\n2. Avatar\n3. Guardar\n4. Cancelar")
            response_whichpartedit = await bot.wait_for('message', check=pred)
            whichpartedit = response_whichpartedit.content

            await char_preview.delete()
            await query_wichpartedit.delete()
            await response_whichpartedit.delete()

        if whichpartedit == '4':
            await ctx.send("Creación del personaje cancelada")
            return
        elif whichpartedit == '3':
            await.ctx.send("Guardando personaje...")
            characterdao.update(shortcut, name, thumbnail, ctx.guild.id)
            return
    else:
        member_role = memberroledao.get(ctx.author.id)
        is_master = member_role != None and member_role.role == 'masta'
        if is_master or not characterdao.exists_player(ctx.author.id):
            query_name = await ctx.send("Escribe el nombre de tu personaje:")
            response_name = await bot.wait_for('message', check=pred)
            name = response_name.content
            await query_name.delete()
            await response_name.delete()

            query_thumbnail = await ctx.send("Escribe la url del avatar de tu personaje:")
            response_thumbnail = await bot.wait_for('message', check=pred)
            thumbnail = response_thumbnail.content
            await query_thumbnail.delete()
            await response_thumbnail.delete()
            await starting_creation.delete()

            if not checkers.is_url(thumbnail):
                error_message = await ctx.send('El valor **{0}** para *thumbnail* no es una URL'.format(thumbnail))
                await asyncio.sleep(10)
                await error_message.delete()
                return
            
            rich = Embed(title="El personaje tendrá el atajo: {0}".format(shortcut), color=0xffffff)
            rich.set_author(name=name)
            rich.set_thumbnail(url=thumbnail)
            
            char_preview = await ctx.send(embed=rich)
            query_confirmation = await ctx.send("Confirma los datos del personaje (s o n):")
            response_confirmation = await bot.wait_for('message', check=pred)
            confirmation = response_confirmation.content
            await char_preview.delete()
            await query_confirmation.delete()
            await response_confirmation.delete()

            if confirmation == 's':
                await ctx.send("Creando el personaje...")
                characterdao.insert(shortcut, name, thumbnail, ctx.author.id, ctx.guild.id)
            else:
                await ctx.send("Creación del personaje cancelada")
        else:
            await ctx.send('No eres el masta y ya tienes un personaje')

@bot.command()
async def char(ctx, shortcut:str="", name:str="", thumbnail:str=""):
    if not checkers.is_url(thumbnail):
        error_message = await ctx.send('El valor **{0}** para *thumbnail* no es una URL'.format(thumbnail))
        await asyncio.sleep(10)
        await error_message.delete()
        return

    if characterdao.exists_shortcut_guild(shortcut, ctx.guild.id):
        characterdao.update(shortcut, name, thumbnail, ctx.guild.id)
    else:
        member_role = memberroledao.get(ctx.author.id)
        is_master = member_role != None and member_role.role == 'masta'
        if is_master or not characterdao.exists_player(ctx.author.id):
            characterdao.insert(shortcut, name, thumbnail, ctx.author.id, ctx.guild.id)
        else:
            await ctx.send('No eres el masta y ya tienes un personaje')

@bot.command()
async def say(ctx, text:str, shortcut:str=''):
    await ctx.message.delete()

    channel_role = channelroledao.get(ctx.channel.id)
    if channel_role == None or (channel_role.role != 'on-rol' and channel_role.role != 'combat'):
        error_message = await ctx.send("Estás en un canal que no pertenece a ON-ROL")
        await asyncio.sleep(5)
        await error_message.delete()
        return

    rich=Embed(title=text, color=0xffffff)

    if shortcut != '':
        player_character = characterdao.get_shortcut_guild(shortcut, ctx.guild.id)
    else:
        player_character = characterdao.get_player_guild(ctx.author.id, ctx.guild.id)

    if player_character != None:
        rich.set_author(name=player_character.name)
        rich.set_thumbnail(url=player_character.thumbnail)

        await ctx.send(embed=rich)
    else:
        result_message = await ctx.send('No tienes ningún personaje asignado o no se encuentra el personaje, utiliza **d!char** para crear tu personaje')
        
        await asyncio.sleep(5)
        await result_message.delete()

@bot.command()
async def combat(ctx, enemy:discord.Member):
    await ctx.message.delete()

    channel_role = channelroledao.get(ctx.channel.id)
    if channel_role == None or channel_role.role != 'combat':
        combat_role = channelroledao.combat()
        combat_channel = bot.get_channel(int(combat_role.channel_id))
        error_message = await ctx.send("Si quieres combatir ve a {0}".format(combat_channel.mention))
        await asyncio.sleep(5)
        await error_message.delete()
        return

    msg = await ctx.send('{0} desafía a {1} a un combate'.format(ctx.author.mention, enemy.mention))
    await msg.pin()

@bot.group()
async def config(ctx):
    pass

@config.command()
async def chrole(ctx, role:str):
    await ctx.message.delete()
    
    if not channelroledao.exists(ctx.channel.id):
        channelroledao.insert(ctx.channel.id, ctx.guild.id, role)
    else:
        channelroledao.update(ctx.channel.id, role)

    await ctx.send('{0} has been assigned **{1}** role'.format(ctx.channel.mention, role))

@config.command()
async def usrole(ctx, role:str, user:discord.Member):
    await ctx.message.delete()
    
    if not memberroledao.exists(user.id):
        memberroledao.insert(user.id, ctx.guild.id, role)
    else:
        memberroledao.update(user.id, role)

    await ctx.send('{0} has been assigned **{1}** role'.format(user.mention, role))

@config.command()
async def userid(ctx, user:discord.Member):
    await ctx.send(user.id)

async def delete_messages(*messages):
    for message in list(messages):
        await message.delete()

bot.run(bot_token)
