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

async def ask_for_information(ctx:Context, bot, text):
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel

    query = await ctx.send(text)
    response = await bot.wait_for('message', check=pred)
    result = response.content
    await delete_messages(query, response)

    return result