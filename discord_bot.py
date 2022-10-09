from datetime import datetime
import sqlite3
import discord
from discord.ext.commands.errors import CommandNotFound
import os
from discord.ext import commands, tasks
from src import league, database
import time
import asyncio

BOT_TOKEN = os.getenv("LEAGUE_OF_GOONS_BOT_TOKEN")
DISCORD_CHANNEL = os.getenv("DISCORD_CHANNEL")
LEAGUE_OF_GOONS_SERVER_ID = int(os.getenv("LEAGUE_OF_GOONS_SERVER"))
K_D_A_MULTIPLIER = int(os.getenv("K_D_A_MULTIPLIER"))
BARON_MULTIPLIER = int(os.getenv("BARON_MULTIPLIER"))
DRAGON_MULTIPLIER = int(os.getenv("DRAGON_MULTIPLIER"))
TURRET_MULTIPLIER = int(os.getenv("TURRET_MULTIPLIER"))
INHIB_MULTIPLIER = int(os.getenv("INHIB_MULTIPLIER"))
WINS_POINTS = int(os.getenv("WINS_POINTS"))
NUMBER_OF_MATCHES = os.getenv("NUMBER_OF_MATCHES")
TASK_TIMER = 5  # Number of minutes (Integer only) Ignore this text

CROWN = os.getenv("CROWN")
POOP = os.getenv("POOP")

help_command = commands.DefaultHelpCommand(
    no_category="Commands",
)

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(
    command_prefix="!",
    case_insensitive=True,
    description="This bot is used to host a tournament amongst those who have enrolled using the !enroll command.\nUse !rules to see the scoring system",
    help_command=help_command,
    intents=intents,
)


@bot.event
async def on_ready():
    print("Bot is ready")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.reply(
            f"WOAH THERE BESSIE\n{ctx.prefix}{ctx.invoked_with} is not a valid command"
        )


@bot.command(brief="Enrolls discord account with Summoner Name")
async def enroll(ctx, *summoner_name: str):
    if summoner_name:
        combined_arguments = " ".join(summoner_name)
        league_info = await league.get_summoner_info(combined_arguments)
        if isinstance(league_info, dict):
            try:
                database.enroll_user(
                    ctx.message.author.name,
                    ctx.message.author.id,
                    league_info["name"],
                    league_info["puuid"],
                    int(time.time()),
                )
                await ctx.reply(
                    f'{league_info["name"]} has been successfully enrolled with {ctx.message.author.name}'
                )
            except sqlite3.IntegrityError:
                league_account = database.get_enrolled_user(ctx.message.author.name)
                await ctx.reply(
                    f"WOAH THERE BESSIE\nYou can't enroll with {combined_arguments} because you are already enrolled with {league_account[0][2]}"
                )
        else:
            await ctx.reply(league_info)
    else:
        await ctx.reply(
            "WOAH THERE BESSIE\nTo use the command type: !enroll <YourSummonerName>"
        )


@enroll.error
async def enroll_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(
            "WOAH THERE BESSIE\nTo use the command type: !enroll <YourSummonerName>"
        )


@bot.command(brief="List all enrolled users")
async def enrolled(ctx):
    response = database.get_enrolled_users()
    if response:
        all_users = database.get_enrolled_users()
        message = discord.Embed(
            title="Enrolled Players",
            description='You can enroll by typing "!enroll <Your Summoner Name>"',
            colour=discord.Color.dark_teal(),
        )
        for user in range(len(all_users)):
            if all_users[user][6]:
                complete_status = all_users[user][2] + " [Completed]"
                message.add_field(name=all_users[user][0], value=complete_status)
            else:
                user_status = f"{all_users[user][2]} [{all_users[user][14]}/{NUMBER_OF_MATCHES}]"
                message.add_field(name=all_users[user][0], value=user_status)
        await ctx.send(embed=message)
    else:
        await ctx.reply("Nobody is enrolled yet\nCalm your horses")


@bot.command(brief="Removes you from the tournament")
async def unenroll(ctx):
    await ctx.reply(database.unenroll_user(ctx.message.author.name))


@bot.command(brief="How to use bot and explain points")
async def rules(ctx):
    embed_message = discord.Embed(
        title="Rules:",
        description='Join by typing "!enroll <Your Summoner Name>"',
        colour=discord.Color.dark_teal(),
    )
    embed_message.add_field(name="GAMES REQUIRED", value=f"[{NUMBER_OF_MATCHES}]")
    embed_message.add_field(
        name="Win", value=f"{str(WINS_POINTS)} points", inline=False
    )
    embed_message.add_field(
        name="Baron", value=f"{str(BARON_MULTIPLIER)} points", inline=False
    )
    embed_message.add_field(
        name="Inhib", value=f"{str(INHIB_MULTIPLIER)} points", inline=False
    )
    embed_message.add_field(
        name="Dragon", value=f"{str(DRAGON_MULTIPLIER)} points", inline=False
    )
    embed_message.add_field(
        name="Turret", value=f"{str(TURRET_MULTIPLIER)} points", inline=False
    )
    embed_message.add_field(
        name="K/D/A",
        value=f"Kills + Assists / Deaths multiplied by {str(K_D_A_MULTIPLIER)}\nNOTE: Points only added if Kills + Assists greater than Deaths. No points for being trash",
        inline=False,
    )
    await ctx.send(embed=embed_message)


@bot.command(brief="@mention the user you would like to kick. Admin use only")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None):
    if member is None:
        await ctx.reply("Must @mention someone on this server")
    else:
        discord_account = database.get_enrolled_user(member.name)
        if discord_account:
            await ctx.reply(database.unenroll_user(discord_account[0][0]))
        else:
            await ctx.reply(f"{member.name} is not enrolled")


@kick.error
async def kick_error(ctx, error):
    await ctx.reply(error)


def complete_user(user: tuple):
    user_matches = database.get_matches_by_user(user[1])
    if len(user_matches) >= database.AMOUNT_OF_GAMES:
        print(
            "Tourney Completed for:",
            user[0],
            "\n---------------------------------------\n",
        )
        database.update_complete_status_by_user(user[1], 1)
        for match in user_matches:
            kills = match[0]
            deaths = match[1]
            assists = match[2]
            win = match[3]
            print(
                "Kills:",
                kills,
                "Deaths:",
                deaths,
                "Assists:",
                assists,
                "**Win**" if win else "**Loss**",
            )
            print()
        return True
    else:
        return False


async def remove_discord_nicknames():
    current_winner_loser = database.get_winner_loser()
    server = bot.get_guild(LEAGUE_OF_GOONS_SERVER_ID)
    if current_winner_loser:
        for player in current_winner_loser:
            member = server.get_member(int(player[1]))
            if member.nick and member.id != server.owner.id:
                await member.edit(nick=None)


async def set_discord_nicknames():
    current_winner_loser = database.get_winner_loser()
    server = bot.get_guild(LEAGUE_OF_GOONS_SERVER_ID)
    if current_winner_loser:
        member1 = server.get_member(int(current_winner_loser[0][1]))
        if member1.id != server.owner.id:
            new_nick = CROWN + member1.name + CROWN
            await member1.edit(nick=new_nick)
        member2 = server.get_member(int(current_winner_loser[1][1]))
        if member2.id != server.owner.id:
            new_nick = POOP + member2.name + POOP
            await member2.edit(nick=new_nick)


@tasks.loop(minutes=TASK_TIMER)
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
                    last_match_time = datetime.fromtimestamp(user[4]).strftime(
                        "%b %d %I:%M:%S %p"
                    )
                    print(
                        f"{user[0]} has classic no matches played since {last_match_time}\n"
                    )
                else:
                    for match in matches:
                        print(match)
                        match_info = league.get_match_info(match)
                        await asyncio.sleep(1)
                        if (
                            match_info["info"]["gameMode"] == "CLASSIC"
                            and match_info["info"]["gameDuration"] >= 600
                        ):
                            for participant in match_info["info"]["participants"]:
                                if participant["puuid"] == user_puuid:
                                    print(
                                        "Game Ended Unix Timestamp in Seconds:",
                                        int(
                                            (match_info["info"]["gameEndTimestamp"])
                                            / 1000
                                        )
                                        + 10,
                                    )
                                    print("Kills:", participant["kills"])
                                    print("Deaths:", participant["deaths"])
                                    print("Assists:", participant["assists"])
                                    print("Champion:", participant["championName"])
                                    print("Win:", participant["win"])
                                    print("Baron Kills:", participant["baronKills"])
                                    print("Dragon Kills:", participant["dragonKills"])
                                    print("Turrets:", participant["turretTakedowns"])
                                    print("Inhibs:", participant["inhibitorTakedowns"])
                                    print(
                                        database.insert_match(
                                            match,
                                            user[1],
                                            participant["kills"],
                                            participant["deaths"],
                                            participant["assists"],
                                            participant["championName"],
                                            participant["win"],
                                            int(
                                                (match_info["info"]["gameEndTimestamp"])
                                                / 1000
                                            ),
                                            participant["baronKills"],
                                            participant["dragonKills"],
                                            participant["turretTakedowns"],
                                            participant["inhibitorTakedowns"],
                                        )
                                    )
                                    print()
                                    database.update_matches_completed_by_user(user[1])
                        else:
                            print("Match not a Classic game\n")
                    last_match = int(
                        (
                            league.get_match_info(matches[0])["info"][
                                "gameEndTimestamp"
                            ]
                            / 1000
                        )
                        + 10
                    )
                    database.update_last_match(user[1], last_match)
                    await asyncio.sleep(1)
                if complete_user(user):
                    tournament_complete_count += 1

            else:
                tournament_complete_count += 1
                complete_user(user)

        if tournament_complete_count == len(data) and len(data) > 2:
            print(f"All users have completed their {database.AMOUNT_OF_GAMES} games\n")
            embed_message = discord.Embed(
                title="TOURNAMENT ENDED\nANNOUNCING SCORES",
                colour=discord.Color.dark_teal(),
            )
            await channel.send(embed=embed_message)
            await asyncio.sleep(3)
            for user in data:
                complete_user_matches = database.get_matches_by_user(user[1])
                score = 0
                total_kills = 0
                total_deaths = 0
                total_assists = 0
                total_wins = 0
                total_barons = 0
                total_dragons = 0
                total_turrets = 0
                total_inhibs = 0
                for match in complete_user_matches:
                    total_kills += match[0]
                    total_deaths += match[1]
                    total_assists += match[2]
                    print(total_assists * 0.75)
                    win = match[3]
                    total_barons += match[4]
                    total_dragons += match[5]
                    total_turrets += match[6]
                    total_inhibs += match[7]
                    if (match[0] + match[2]) > match[1]:
                        if match[1] > 0:
                            score += int(
                                ((match[0] + match[2]) / match[1]) * K_D_A_MULTIPLIER
                            )
                        else:
                            score += int((match[0] + match[2]) * K_D_A_MULTIPLIER)
                    if win:
                        total_wins += 1
                        score += WINS_POINTS
                score += total_barons * BARON_MULTIPLIER
                score += total_dragons * DRAGON_MULTIPLIER
                score += total_turrets * TURRET_MULTIPLIER
                score += total_turrets * INHIB_MULTIPLIER
                database.update_score_by_user(
                    user[1],
                    score,
                    total_kills,
                    total_deaths,
                    total_assists,
                    total_wins,
                    total_barons,
                    total_dragons,
                    total_turrets,
                    total_inhibs,
                )

            complete_users = database.get_enrolled_users()
            await remove_discord_nicknames()
            database.insert_into_winner_loser(
                complete_users[0][0], complete_users[0][1], complete_users[0][5]
            )
            database.insert_into_winner_loser(
                complete_users[-1][0], complete_users[-1][1], complete_users[-1][5]
            )
            await set_discord_nicknames()

            # Sends embeded message to the discord channel with Crowns for the winners and Poop emojis for the loser.
            print(f"{complete_users[0][0]}: [{complete_users[0][5]}]")
            embed_message = discord.Embed(
                title=f"{CROWN}{complete_users[0][0]}{CROWN}: [{complete_users[0][5]}]",
                colour=discord.Color.dark_teal(),
            )
            embed_message.add_field(name="Total Kills", value=complete_users[0][7])
            embed_message.add_field(name="Total Deaths", value=complete_users[0][8])
            embed_message.add_field(name="Total Assists", value=complete_users[0][9])
            embed_message.add_field(name="Total Barons", value=complete_users[0][11])
            embed_message.add_field(name="Total Dragons", value=complete_users[0][12])
            embed_message.add_field(name="Total Turrets", value=complete_users[0][13])
            embed_message.add_field(name="Total Inhibs", value=complete_users[0][15])
            embed_message.add_field(name="Total Wins", value=complete_users[0][10])
            await channel.send(embed=embed_message)
            await asyncio.sleep(3)
            for user in complete_users[1:-1]:
                print(f"{user[0]}: [{user[5]}]")
                embed_message = discord.Embed(
                    title=f"{user[0]}: [{user[5]}]", colour=discord.Color.dark_teal()
                )
                embed_message.add_field(name="Total Kills", value=user[7])
                embed_message.add_field(name="Total Deaths", value=user[8])
                embed_message.add_field(name="Total Assists", value=user[9])
                embed_message.add_field(name="Total Barons", value=user[11])
                embed_message.add_field(name="Total Dragons", value=user[12])
                embed_message.add_field(name="Total Turrets", value=user[13])
                embed_message.add_field(name="Total Inhibs", value=user[15])
                embed_message.add_field(name="Total Wins", value=user[10])
                await channel.send(embed=embed_message)
                await asyncio.sleep(3)
            print(f"{complete_users[-1][0]}: [{complete_users[-1][5]}]")
            embed_message = discord.Embed(
                title=f"{POOP}{complete_users[-1][0]}{POOP}: [{complete_users[-1][5]}]",
                colour=discord.Color.dark_teal(),
            )
            embed_message.add_field(name="Total Kills", value=complete_users[-1][7])
            embed_message.add_field(name="Total Deaths", value=complete_users[-1][8])
            embed_message.add_field(name="Total Assists", value=complete_users[-1][9])
            embed_message.add_field(name="Total Barons", value=complete_users[-1][11])
            embed_message.add_field(name="Total Dragons", value=complete_users[-1][12])
            embed_message.add_field(name="Total Turrets", value=complete_users[-1][13])
            embed_message.add_field(name="Total Inhibs", value=complete_users[-1][15])
            embed_message.add_field(name="Total Wins", value=complete_users[-1][10])
            await channel.send(embed=embed_message)
            await asyncio.sleep(3)

            # Clear the matches and players database to start a new tournament
            database.clear_matches_and_players()


if __name__ == "__main__":
    results.start()
    bot.run(BOT_TOKEN)
