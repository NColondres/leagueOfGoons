from dotenv import dotenv_values
from discord.ext import commands

BOT_TOKEN = dotenv_values(".env")['LEAGUE_OF_GOONS_BOT_TOKEN']


bot = commands.Bot(command_prefix='!')

@bot.command()
async def test(ctx):
    await ctx.reply(f'Hello {ctx.message.author}')
    await ctx.send(content= ctx.message)
    

async def enroll():
    pass

bot.run(BOT_TOKEN)
