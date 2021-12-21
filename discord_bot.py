from datetime import datetime
import sqlite3
import discord
from discord.ext.commands.errors import CommandNotFound
from dotenv import dotenv_values
from discord.ext import commands, tasks
from src import league, database
import time

BOT_TOKEN = dotenv_values(".env")['LEAGUE_OF_GOONS_BOT_TOKEN']
DISCORD_CHANNEL = dotenv_values('.env')['DISCORD_CHANNEL']
TASK_TIMER = 30
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

def complete_user(user: tuple):
    user_matches = database.get_matches_by_user(user[1])
    if len(user_matches) >= database.AMOUNT_OF_GAMES:
        print('Tourney Completed for:', user[0],'\n---------------------------------------\n')
        database.update_complete_status_by_user(user[1], 1)
        for match in user_matches:
            kills = match[0]
            deaths = match[1]
            assists = match[2]
            win = match[3]
            print( 'Kills:', kills, 'Deaths:', deaths, 'Assists:', assists, '**Win**' if win else '**Loss**')
            print()
        return True
    else:
        return False


@tasks.loop(minutes = TASK_TIMER)
async def results():
    await bot.wait_until_ready()
    channel = bot.get_channel(int(DISCORD_CHANNEL))
    data = database.get_enrolled_users()
    if data:
        tournament_complete_count = 0
        for user in data:
            if not user[6]:
                user_puuid = user[3]
                matches = league.get_league_matches(user_puuid, str(user[4]))
                if not matches:
                    last_match_time = datetime.fromtimestamp(user[4]).strftime('%b %d %I:%M:%S %p')
                    print(f'{user[0]} has classic no matches played since {last_match_time}\n')
                else:
                    for match in matches:
                        print(match)
                        match_info = league.get_match_info(match)
                        time.sleep(1)
                        if match_info['info']['gameMode'] == 'CLASSIC':
                            for participant in match_info['info']['participants']:
                                if participant['puuid'] == user_puuid:
                                    print('Game Ended Unix Timestamp in Seconds:', int((match_info['info']['gameEndTimestamp']) / 1000) + 10)
                                    print('Kills:', participant['kills'])
                                    print('Deaths:', participant['deaths'])
                                    print('Assists:', participant['assists'])
                                    print('Champion:', participant['championName'])
                                    print('Win:', participant['win'])
                                    database.insert_match(match, user[1], participant['kills'], participant['deaths'], participant['assists'], participant['championName'], participant['win'], int((match_info['info']['gameEndTimestamp']) / 1000))
                                    print()
                        else:
                            print('Match not a Classic game\n')
                    last_match = int((league.get_match_info(matches[0])['info']['gameEndTimestamp'] / 1000) + 10)
                    database.update_last_match(user[1], last_match)
                    time.sleep(1)
                if complete_user(user):
                    tournament_complete_count += 1

            else:
                tournament_complete_count += 1
                complete_user(user)
            

        if tournament_complete_count == len(data):
            print(f'All users have completed their {database.AMOUNT_OF_GAMES} games\n')
            embed_message = discord.Embed(title='TOURNAMENT ENDED\nANNOUNCING SCORES', colour=discord.Color.dark_teal())
            await channel.send(embed = embed_message)
            for user in data:
                complete_user_matches = database.get_matches_by_user(user[1])
                score = 0
                for match in complete_user_matches:
                    kills = match[0]
                    deaths = match[1]
                    assists = match[2]
                    win = match[3]
                    if (kills + assists) / deaths >= 1:
                        if deaths > 0:
                            score += int(((kills + assists) / deaths) * 100)
                        else:
                            score += int((kills + assists) * 100)
                    if win:
                        score += 2000
                database.update_score_by_user(user[1], score)
                print(f'{user[0]} has a score of [{score}]')
                embed_message = discord.Embed(title=f'{user[0]}: [{score}]', colour=discord.Color.dark_teal())
                await channel.send(embed = embed_message)
            await bot.close()
                
                                
            
    else:
        print('Nobody is enrolled yet')

if __name__ == '__main__':    
    results.start()
    bot.run(BOT_TOKEN)