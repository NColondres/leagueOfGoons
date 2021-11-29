from discord.ext.commands.errors import CommandNotFound
from dotenv import dotenv_values
from discord.ext import commands
from src import league, database

BOT_TOKEN = dotenv_values(".env")['LEAGUE_OF_GOONS_BOT_TOKEN']

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.reply(f'You fucked up...\n{ctx.prefix}{ctx.invoked_with} is not a valid command')

@bot.command()
async def enroll(ctx, summoner_name: str):
    league_info = await league.get_summoner_info(summoner_name)
    database.enroll_user(ctx.message.author, ctx.message.author.id, league_info["name"], league_info["puuid"])
    await ctx.reply(f'{league_info["name"]} has been enrolled with {ctx.message.author}')

@enroll.error
async def enroll_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply('You fucked up...\nTo use the command type: !enroll <YourSummonerName>')

@bot.command()
async def enrolled(ctx):
    await ctx.send(database.get_enrolled_users())

bot.run(BOT_TOKEN)
