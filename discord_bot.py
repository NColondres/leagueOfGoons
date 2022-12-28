import sqlite3
import discord
from discord.ext.commands.errors import CommandNotFound
import os
from discord.ext import commands, tasks
from src import league, database
import time
import asyncio
import configparser

# Read config file in root directory
config = configparser.ConfigParser()
config.read(f"{os.getcwd()}/config")
scoring = config["SCORING"]

BOT_TOKEN = os.getenv("LEAGUE_OF_GOONS_BOT_TOKEN")
DISCORD_CHANNEL = os.getenv("DISCORD_CHANNEL")
LEAGUE_OF_GOONS_SERVER_ID = int(os.getenv("LEAGUE_OF_GOONS_SERVER"))
MINIMUM_PLAYERS = int(config["RULES"]["MINIMUM_PLAYERS"])
K_D_A_MULTIPLIER = int(scoring["K_D_A_MULTIPLIER"])
BARON_MULTIPLIER = int(scoring["BARON_MULTIPLIER"])
DRAGON_MULTIPLIER = int(scoring["DRAGON_MULTIPLIER"])
TURRET_MULTIPLIER = int(scoring["TURRET_MULTIPLIER"])
INHIB_MULTIPLIER = int(scoring["INHIB_MULTIPLIER"])
RIFT_MULTIPLIER = int(scoring["RIFT_MULTIPLIER"])
PENTA_MULTIPLIER = int(scoring["PENTA_MULTIPLIER"])
VISION_MULTIPLIER = int(scoring["VISION_MULTIPLIER"])
CREEP_MULTIPLIER = float(scoring["CREEP_SCORE"])
WINS_POINTS = int(scoring["WINS_POINTS"])
NUMBER_OF_MATCHES = config["RULES"]["NUMBER_OF_MATCHES"]
TASK_TIMER = 1  # Number of minutes to run task

emoji = config["EMOJI"]
CROWN = emoji["CROWN"]
POOP = emoji["POOP"]

help_command = commands.DefaultHelpCommand(
    no_category="Commands",
)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
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
    results.start()


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
                    int(time.time()) + 600,
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
    all_users = database.get_enrolled_users()
    if all_users:
        message = discord.Embed(
            title="Enrolled Players",
            description='You can enroll by typing "!enroll <Your Summoner Name>"',
            colour=discord.Color.dark_teal(),
        )
        for user in range(len(all_users)):
            if all_users[user]["complete_status"]:
                complete_status = all_users[user]["league_account"] + " [Completed]"
                message.add_field(
                    name=all_users[user]["discord_account"], value=complete_status
                )
            else:
                user_status = f"{all_users[user]['league_account']} [{all_users[user]['matches_completed']}/{NUMBER_OF_MATCHES}]"
                message.add_field(
                    name=all_users[user]["discord_account"], value=user_status
                )
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
        name="Rift", value=f"{str(RIFT_MULTIPLIER)} points", inline=False
    )
    embed_message.add_field(
        name="Penta", value=f"{str(PENTA_MULTIPLIER)} points", inline=False
    )
    embed_message.add_field(
        name="Vision Score", value=f"{str(VISION_MULTIPLIER)} points", inline=False
    )
    embed_message.add_field(
        name="Creep Score", value=f"{str(CREEP_MULTIPLIER)} points", inline=False
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
    user_matches = database.get_matches_by_user(user["discord_id"])
    if len(user_matches) >= database.AMOUNT_OF_GAMES:
        print(
            "Tourney Completed for:",
            user["discord_account"],
            "\n---------------------------------------\n",
        )
        database.update_complete_status_by_user(user["discord_id"], 1)
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
        if member1 and member1.id != server.owner.id:
            new_nick = CROWN + member1.name + CROWN
            await member1.edit(nick=new_nick)
        member2 = server.get_member(int(current_winner_loser[1][1]))
        if member2 and member2.id != server.owner.id:
            new_nick = POOP + member2.name + POOP
            await member2.edit(nick=new_nick)


def calculate_kda(kills: int, deaths: int, assists: int) -> str:
    # Assists count for 70% of a kill.
    if (kills + assists) > deaths:
        if deaths > 0:
            return int(((kills + int(assists * 0.70)) / deaths) * K_D_A_MULTIPLIER)
        else:
            return int((kills + int(assists * 0.70)) * K_D_A_MULTIPLIER)
    return 0


@tasks.loop(minutes=TASK_TIMER)
async def results():
    await bot.wait_until_ready()
    channel = bot.get_channel(int(DISCORD_CHANNEL))
    data = database.get_enrolled_users()
    if data:
        tournament_complete_count = 0
        for user in data:
            if not user["complete_status"]:
                user_puuid = user["league_puuid"]
                matches = league.get_league_matches(user_puuid, str(user["last_match"]))
                if not matches:
                    continue
                elif matches == 503:
                    print("503 Error: League API is down")
                else:
                    match_count = 0
                    for match in matches:
                        if match_count == int(NUMBER_OF_MATCHES):
                            break
                        match_info = league.get_match_info(match)
                        await asyncio.sleep(1)
                        if (
                            match_info["info"]["gameMode"] == "CLASSIC"
                            and match_info["info"]["gameDuration"] >= 600
                        ):
                            for participant in match_info["info"]["participants"]:
                                if participant["puuid"] == user_puuid:
                                    print(
                                        "Completed game for:", user["discord_account"]
                                    )
                                    print("Kills:", participant["kills"])
                                    print("Deaths:", participant["deaths"])
                                    print("Assists:", participant["assists"])
                                    print("Champion:", participant["championName"])
                                    print("Win:", participant["win"])
                                    print(
                                        "Baron Kills:",
                                        participant["challenges"]["baronTakedowns"],
                                    )
                                    print(
                                        "Dragon Kills:",
                                        participant["challenges"]["dragonTakedowns"],
                                    )
                                    print("Turrets:", participant["turretTakedowns"])
                                    print("Inhibs:", participant["inhibitorTakedowns"])
                                    print(
                                        "Rifts:",
                                        participant["challenges"][
                                            "riftHeraldTakedowns"
                                        ],
                                    )
                                    print("Pentas:", participant["pentaKills"])
                                    print("Vision Score:", participant["visionScore"])
                                    print(
                                        "Creep Score:",
                                        participant["neutralMinionsKilled"]
                                        + participant["totalMinionsKilled"],
                                    )
                                    print(
                                        database.insert_match(
                                            match,
                                            user["discord_id"],
                                            participant["kills"],
                                            participant["deaths"],
                                            participant["assists"],
                                            participant["championName"],
                                            participant["win"],
                                            int(
                                                (match_info["info"]["gameEndTimestamp"])
                                                / 1000
                                            ),
                                            participant["challenges"]["baronTakedowns"],
                                            participant["challenges"][
                                                "dragonTakedowns"
                                            ],
                                            participant["turretTakedowns"],
                                            participant["inhibitorTakedowns"],
                                            participant["challenges"][
                                                "riftHeraldTakedowns"
                                            ],
                                            participant["pentaKills"],
                                            participant["visionScore"],
                                            participant["neutralMinionsKilled"]
                                            + participant["totalMinionsKilled"],
                                        )
                                    )
                                    print()
                                    database.update_matches_completed_by_user(
                                        user["discord_id"]
                                    )
                            match_count += 1
                        else:
                            print(
                                f"{match} is not a 'Classic' game or not longer than 10 minutes\n"
                            )
                    last_match = int(
                        (
                            league.get_match_info(matches[0])["info"][
                                "gameEndTimestamp"
                            ]
                            / 1000
                        )
                        + 10
                    )
                    database.update_last_match(user["discord_id"], last_match)
                    await asyncio.sleep(1)
                if complete_user(user):
                    tournament_complete_count += 1

            else:
                tournament_complete_count += 1

        if tournament_complete_count == len(data) and len(data) >= MINIMUM_PLAYERS:
            print(f"All users have completed their {database.AMOUNT_OF_GAMES} games\n")
            embed_message = discord.Embed(
                title="TOURNAMENT ENDED\nANNOUNCING SCORES",
                colour=discord.Color.dark_teal(),
            )
            await channel.send(embed=embed_message)
            await asyncio.sleep(2)
            for user in data:
                complete_user_matches = database.get_matches_by_user(user["discord_id"])
                score = 0
                kda_score = 0
                total_kills = 0
                total_deaths = 0
                total_assists = 0
                total_wins = 0
                total_barons = 0
                total_dragons = 0
                total_turrets = 0
                total_inhibs = 0
                total_rifts = 0
                total_pentas = 0
                total_vision_score = 0
                total_creep_score = 0
                for match in complete_user_matches:
                    total_kills += match[0]
                    total_deaths += match[1]
                    total_assists += match[2]
                    win = match[3]
                    total_barons += match[4]
                    total_dragons += match[5]
                    total_turrets += match[6]
                    total_inhibs += match[7]
                    total_rifts += match[8]
                    total_pentas += match[9]
                    total_vision_score += match[10]
                    total_creep_score += match[11]
                    # Assists count for 70% of a kill.
                    kda = calculate_kda(match[0], match[1], match[2])
                    kda_score += kda
                    score += kda
                    if win:
                        total_wins += 1
                        score += WINS_POINTS
                score += total_barons * BARON_MULTIPLIER
                score += total_dragons * DRAGON_MULTIPLIER
                score += total_turrets * TURRET_MULTIPLIER
                score += total_inhibs * INHIB_MULTIPLIER
                score += total_rifts * RIFT_MULTIPLIER
                score += total_pentas * PENTA_MULTIPLIER
                score += total_vision_score * VISION_MULTIPLIER
                score += int(total_creep_score * CREEP_MULTIPLIER)
                database.update_score_by_user(
                    user["discord_id"],
                    score,
                    total_kills,
                    total_deaths,
                    total_assists,
                    total_wins,
                    total_barons,
                    total_dragons,
                    total_turrets,
                    total_inhibs,
                    kda_score,
                    total_rifts,
                    total_pentas,
                    total_vision_score,
                    total_creep_score,
                )

            complete_users = database.get_enrolled_users()
            await remove_discord_nicknames()
            database.insert_into_winner_loser(
                complete_users[0]["discord_account"],
                complete_users[0]["discord_id"],
                complete_users[0]["score"],
            )
            database.insert_into_winner_loser(
                complete_users[-1]["discord_account"],
                complete_users[-1]["discord_id"],
                complete_users[-1]["score"],
            )
            await set_discord_nicknames()

            # Sends embeded message to the discord channel with Crowns for the winners and Poop emojis for the loser.
            for count, user in enumerate(complete_users):
                if count == 0:
                    embed_message = discord.Embed(
                        title=f"{CROWN}{complete_users[0]['discord_account']}{CROWN}: [{complete_users[0]['score']}]",
                        colour=discord.Color.dark_teal(),
                    )
                elif count == len(complete_users) - 1:
                    embed_message = discord.Embed(
                        title=f"{POOP}{complete_users[-1]['discord_account']}{POOP}: [{complete_users[-1]['score']}]",
                        colour=discord.Color.dark_teal(),
                    )
                else:
                    embed_message = discord.Embed(
                        title=f"{user['discord_account']}: [{user['score']}]",
                        colour=discord.Color.dark_teal(),
                    )
                print(f"{user['discord_account']}: [{user['score']}]")
                k_d_a = (
                    "/".join(
                        map(
                            str,
                            (
                                user["total_kills"],
                                user["total_deaths"],
                                user["total_assists"],
                            ),
                        )
                    )
                    + "\n("
                    + str(user["kda_score"])
                    + ")"
                )
                embed_message.add_field(name="K/D/A", value=k_d_a)
                baron_message = f"{user['total_barons']} ({user['total_barons'] * BARON_MULTIPLIER})"
                embed_message.add_field(name="Barons", value=baron_message)
                dragon_message = f"{user['total_dragons']} ({user['total_dragons'] * DRAGON_MULTIPLIER})"
                embed_message.add_field(name="Dragons", value=dragon_message)
                turret_message = f"{user['total_turrets']} ({user['total_turrets'] * TURRET_MULTIPLIER})"
                embed_message.add_field(name="Turrets", value=turret_message)
                inhibs_message = f"{user['total_inhibs']} ({user['total_inhibs'] * INHIB_MULTIPLIER})"
                embed_message.add_field(name="Inhibs", value=inhibs_message)
                rift_message = (
                    f"{user['total_rifts']} ({user['total_rifts'] * RIFT_MULTIPLIER})"
                )
                embed_message.add_field(name="Rifts", value=rift_message)
                # Show pentas if user actually got one.
                if user["total_pentas"] > 0:
                    penta_message = f"{user['total_pentas']} ({user['total_pentas'] * PENTA_MULTIPLIER})"
                    embed_message.add_field(name="PENTAS", value=penta_message)
                vision_message = f"{user['total_vision_score']} ({user['total_vision_score'] * VISION_MULTIPLIER})"
                embed_message.add_field(name="Vision", value=vision_message)
                creep_message = f"{user['total_creep_score']} ({int(user['total_creep_score'] * CREEP_MULTIPLIER)})"
                embed_message.add_field(name="Creeps", value=creep_message)
                wins_message = (
                    f"{user['total_wins']} ({user['total_wins'] * WINS_POINTS})"
                )
                embed_message.add_field(name="Wins", value=wins_message)
                await channel.send(embed=embed_message)
                await asyncio.sleep(2)

            # Clear the matches and players database to start a new tournament
            database.clear_matches_and_players()


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
