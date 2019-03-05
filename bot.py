import discord
import random
import utils
import asyncio
import configparser
import os
import psycopg2
from validator_collection import checkers
from discord.ext import commands
from discord.ext.commands import Context
from discord import Embed
from discord import Client
from database import characterdao
from database import channelroledao
from database import memberroledao
from rules.dxd import DxD

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
async def lchars(ctx:Context):
    characters = characterdao.get_all_player(ctx.author.id, ctx.guild.id)

    for character in characters:
        rich = Embed(title = '', color=0xffffff)
        rich.add_field(name = 'Nombre', value = character.name)
        rich.add_field(name = 'Atajo', value = character.shortcut)
        rich.set_thumbnail(url = character.thumbnail)

        await ctx.send(embed = rich)

@bot.command()
async def char(ctx:Context):
    shortcut = await utils.ask_for_information(ctx, bot, "Escribe un atajo para referirte a tu personaje:")

    return_message = None
    if characterdao.exists_shortcut_guild(shortcut, ctx.guild.id):
        character = characterdao.get_shortcut_guild(shortcut, ctx.guild.id)

        shortcut = character.shortcut
        name = character.name
        thumbnail = character.thumbnail

        rich = Embed(title = 'Vista previa del personaje', color=0xffffff)
        rich.add_field(name = 'Nombre', value = name)
        rich.add_field(name = 'Atajo', value = shortcut)
        rich.set_thumbnail(url=thumbnail)

        char_preview = await ctx.send(embed=rich)

        which_part_edit = await utils.ask_for_information(ctx, bot, "Elige el número del atributo que quieres cambiar:\n1. Nombre\n2. Avatar\n3. Guardar\n4. Cancelar")

        while which_part_edit != '4' and which_part_edit != '3':
            if which_part_edit == '2':
                thumbnail = await utils.ask_for_information(ctx, bot, "Escribe la url del avatar de tu personaje:")

                if not checkers.is_url(thumbnail):
                    error_message = await ctx.send('El valor **{0}** para *thumbnail* no es una URL'.format(thumbnail))
                    await asyncio.sleep(10)
                    await utils.delete_messages(error_message)
                    return
            elif which_part_edit == '1':
                name = await utils.ask_for_information(ctx, bot,  "Escribe el nombre de tu personaje:")

            await utils.delete_messages(char_preview)
            rich = Embed(title = 'Vista previa del personaje', color=0xffffff)
            rich.add_field(name = 'Nombre', value = name)
            rich.add_field(name = 'Atajo', value = shortcut)
            rich.set_thumbnail(url=thumbnail)

            char_preview = await ctx.send(embed=rich)
            which_part_edit = await utils.ask_for_information(ctx, bot, "Elige el número del atributo que quieres cambiar:\n1. Nombre\n2. Avatar\n3. Guardar\n4. Cancelar")

        await utils.delete_messages(char_preview)

        if which_part_edit == '4':
            return_message = await ctx.send("Creación del personaje cancelada")
        elif which_part_edit == '3':
            return_message = await ctx.send("Guardando personaje...")
            characterdao.update(shortcut, name, thumbnail, ctx.guild.id)
    else:
        member_role = memberroledao.get(ctx.author.id, ctx.guild.id)
        is_master = member_role != None and member_role.role == 'masta'
        if is_master or not characterdao.exists_player_guild(ctx.author.id, ctx.guild.id):
            starting_creation = await ctx.send("{0.author.display_name} comienza la creación de un personaje".format(ctx))
            
            name = await utils.ask_for_information(ctx, bot, "Escribe el nombre de tu personaje:")

            thumbnail = await utils.ask_for_information(ctx, bot, "Escribe la url del avatar de tu personaje:")

            if not checkers.is_url(thumbnail):
                error_message = await ctx.send('El valor **{0}** para *thumbnail* no es una URL'.format(thumbnail))
                await asyncio.sleep(10)
                await utils.delete_messages(error_message)
                return

            await utils.delete_messages(starting_creation)
            
            rich = Embed(title = 'Vista previa del personaje', color=0xffffff)
            rich.add_field(name = 'Nombre', value = name)
            rich.add_field(name = 'Atajo', value = shortcut)
            rich.set_thumbnail(url=thumbnail)
            
            char_preview = await ctx.send(embed=rich)
            confirmation = await utils.ask_for_information(ctx, bot, "Confirma los datos del personaje (s o n):")

            if confirmation == 's':
                return_message = await ctx.send("Creando el personaje...")
                characterdao.insert(shortcut, name, thumbnail, ctx.author.id, ctx.guild.id)
            else:
                return_message = await ctx.send("Creación del personaje cancelada")
        else:
            return_message = await ctx.send('No eres el masta y ya tienes un personaje')

    if return_message != None:
        await utils.delete_messages(return_message, ctx.message)
    else:
        await utils.delete_messages(ctx.message)

@bot.command()
async def say(ctx:Context, character_shortcut:str=''):
    await ctx.message.delete()

    channel_role = channelroledao.get(ctx.channel.id)
    if channel_role == None or (channel_role.role != 'on-rol' and channel_role.role != 'combat'):
        error_message = await ctx.send('Estás en un canal que no pertenece a ON-ROL')
        await asyncio.sleep(5)
        await error_message.delete()
        return

    if character_shortcut != '':
        player_character = characterdao.get_shortcut_player_guild(character_shortcut, ctx.author.id, ctx.guild.id)
    else:
        player_character = characterdao.get_player_guild(ctx.author.id, ctx.guild.id)

    if player_character != None:
        async with ctx.typing():
            text = await utils.ask_for_information(ctx, bot, '¿Qué vas a decir?')

            rich = Embed(title = text, color = 0xffffff)
            rich.set_author(name = player_character.name)
            rich.set_thumbnail(url = player_character.thumbnail)

            await ctx.send(embed = rich)
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

    player_character_challenger = characterdao.get_player_guild(ctx.author.id, ctx.guild.id)
    player_character_challenged = characterdao.get_player_guild(enemy.id, ctx.guild.id)

    if player_character_challenger != None and player_character_challenged != None:
        challenge_answer = await utils.ask_for_information(ctx, bot, '{0}, ¿quieres aceptar el combate con {1}? (S/N)'.format(enemy.mention, ctx.author.mention), 25, enemy)

        while challenge_answer != 'S' or challenge_answer != 'N' or challenge_answer != '**':
            challenge_answer = await utils.ask_for_information(ctx, bot, 'No entiendo **{0}**, {1}, ¿quieres aceptar el combate con {2}? (S/N)'.format(challenge_answer, enemy.mention, ctx.author.mention), 25, enemy)

        if challenge_answer == 'S':
            msg = await ctx.send('**{0}** desafía a **{1}** a un combate'.format(player_character_challenger.name, player_character_challenged.name))
            await msg.pin()
        elif challenge_answer == 'N':
            msg = await ctx.send('**{0}** ha rechazado la petición de **{1}** a un combate'.format(player_character_challenged.name, player_character_challenger.name))
            await utils.delete_messages(msg)
        elif challenge_answer == '':
            msg = await ctx.send('Se ha acabado el tiempo de espera volved a realizar el reto')
            await utils.delete_messages(msg)
    elif player_character_challenger == None:
        msg = await ctx.send('{0}, no tienes personaje creado, por favor crealo con d!char'.format(ctx.author.mention))
        await utils.delete_messages(msg)
    elif player_character_challenged == None:
        msg = await ctx.send('{0}, no tienes personaje creado, por favor crealo con d!char'.format(enemy.mention))
        await utils.delete_messages(msg)

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
    
    if not memberroledao.exists(user.id, ctx.guild.id):
        memberroledao.insert(user.id, ctx.guild.id, role)
    else:
        memberroledao.update(user.id, role)

    await ctx.send('{0} has been assigned **{1}** role'.format(user.mention, role))

@config.command()
async def userid(ctx, user:discord.Member):
    await ctx.send(user.id)

@config.command()
async def chunni_god(ctx:Context):
    await ctx.send('https://media1.tenor.com/images/270f9074cc8766817760111de4f5b71c/tenor.gif?itemid=5820863')

bot.run(bot_token)
