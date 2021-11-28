from logging import error
from discord.ext.commands.errors import CommandNotFound
from dotenv import dotenv_values
from discord.ext import commands
from src import league, database

BOT_TOKEN = dotenv_values(".env")['LEAGUE_OF_GOONS_BOT_TOKEN']

database.create_database('players_data.db')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.reply(f'You fucked up...\n{ctx.prefix}{ctx.invoked_with} is not a valid command')

@bot.command()
async def enroll(ctx, summoner_name: str):
    await ctx.reply(f'{ctx.message.author}: {ctx.message.author.id}')
    await ctx.send(league.get_summoner_info(summoner_name))

@enroll.error
async def enroll_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply('You fucked up...\nTo use the command type: !enroll <YourSummonerName>')

async def test():
    pass

bot.run(BOT_TOKEN)
