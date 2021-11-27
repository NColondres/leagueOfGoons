from discord.ext import commands
TOKEN = 'OTA5MTQ3ODAzOTY2NjQwMTU4.YZAD3w.A4J2kwl9pQXvKQcMs2gpQ6DvMqo'

bot = commands.Bot(command_prefix='!')

@bot.command()
async def test(ctx):
    await ctx.reply(f'Hello {ctx.message.author}')
    await ctx.send(content= ctx.message)

async def enroll():
    pass

bot.run(TOKEN)
