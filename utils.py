import asyncio
from discord.ext.commands import Context

def is_int(x):
    try:
        int(x)
        return True
    except ValueError:
        return False

async def delete_messages(*messages):
    for message in list(messages):
        await message.delete()

async def ask_for_information(ctx:Context, bot, text, timeout=None, user=None):
    def pred(m):
        if user != None: 
            return m.author == user and m.channel == ctx.channel
        return m.author == ctx.author and m.channel == ctx.channel

    query = await ctx.send(text)
    try:
        response = await bot.wait_for('message', check=pred, timeout=timeout)
        result = response.content
        await delete_messages(query, response)
    except asyncio.TimeoutError:
        result = ''
        await delete_messages(query)

    return result