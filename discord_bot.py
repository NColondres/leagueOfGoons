from os import name
import sqlite3
import discord
from discord.ext.commands.errors import CommandNotFound
from dotenv import dotenv_values
from discord.ext import commands
from src import league, database
import time

BOT_TOKEN = dotenv_values(".env")['LEAGUE_OF_GOONS_BOT_TOKEN']
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.reply(f'WOAH THERE BESSIE\n{ctx.prefix}{ctx.invoked_with} is not a valid command')

@bot.command()
async def enroll(ctx, *summoner_name: str):
    if summoner_name:
        combined_arguments = ' '.join(summoner_name)
        league_info = await league.get_summoner_info(combined_arguments)
        if isinstance(league_info, dict):
            try:
                database.enroll_user(ctx.message.author, ctx.message.author.id, league_info["name"], league_info["puuid"], int(time.time()))
                await ctx.reply(f'{league_info["name"]} has been successfully enrolled with {ctx.message.author}')
            except sqlite3.IntegrityError as err:
                league_account = database.get_enrolled_user(ctx.message.author)
                await ctx.reply(f'WOAH THERE BESSIE\nYou can\'t enroll with {combined_arguments} because you are already enrolled with {league_account[0][2]}')
        else:
            await ctx.reply(league_info)
    else:
        await ctx.reply('WOAH THERE BESSIE\nTo use the command type: !enroll <YourSummonerName>')

@enroll.error
async def enroll_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply('WOAH THERE BESSIE\nTo use the command type: !enroll <YourSummonerName>')

@bot.command()
async def enrolled(ctx):
    response = database.get_enrolled_users()
    if response:
        all_users = database.get_enrolled_users()
        message = discord.Embed(title='Enrolled Players', description='You can enroll by typing "!enroll <Your Summoner Name>"', colour=discord.Color.dark_teal())
        for user in range(len(all_users)):
            message.add_field(name=all_users[user][0], value=all_users[user][2])
        await ctx.send(embed=message)   
    else:
        await ctx.reply('Nobody is enrolled yet\nCalm your horses')

@bot.command()
async def unenroll(ctx):
    await ctx.reply(database.unenroll_user(ctx.message.author))


if __name__ == '__main__':
    bot.run(BOT_TOKEN)