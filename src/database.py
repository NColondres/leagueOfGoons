import sqlite3
import configparser
import os
print("databse.py cwd:", os.getcwd())
config = configparser.ConfigParser()
config.read("/app/config")
scoring = config["SCORING"]
PLAYERS_DATABASE = "players_data.db"
AMOUNT_OF_GAMES = int(scoring["NUMBER_OF_MATCHES"])


def create_database(name: str):
    con = sqlite3.connect(f"./src/database/{name}")
    cur = con.cursor()
    # Create Table
    cur.execute(
        """CREATE TABLE IF NOT EXISTS players(
                discord_account text PRIMARY KEY,
                discord_id text UNIQUE,
                league_account text UNIQUE,
                league_puuid text UNIQUE,
                last_match INTEGER,
                score INTEGER DEFAULT 0,
                complete_status INTEGER DEFAULT 0 NOT NULL,
                total_kills INTEGER,
                total_deaths INTEGER,
                total_assists INTEGER,
                total_wins INTEGER,
                total_barons INTEGER,
                total_dragons INTEGER,
                total_turrets INTEGER,
                matches_completed INTEGER DEFAULT 0 NOT NULL,
                total_inhibs INTEGER,
                kda_score INTEGER,
                total_rifts INTEGER,
                total_pentas INTEGER,
                total_vision_score INTEGER);
                """
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS matches(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                player_id TEXT,
                kills INTEGER,
                deaths INTEGER,
                assists INTEGER,
                champion TEXT,
                win INTEGER,
                match_end_timestamp INTEGER NOT NULL,
                barons INTEGER,
                dragons INTEGER,
                turrets INTEGER,
                inhibs INTEGER,
                pentas INTEGER,
                rifts INTEGER,
                vision_score INTEGER
                FOREIGN KEY(player_id) REFERENCES players(discord_id));"""
    )
    cur.execute(
        """
                CREATE TABLE IF NOT EXISTS winner_loser(
                discord_account TEXT,
                discord_id TEXT PRIMARY KEY,
                score INTEGER);
    """
    )
    con.commit()
    con.close()


create_database(PLAYERS_DATABASE)


def enroll_user(
    discord_account: str,
    discord_id: str,
    league_account: str,
    league_puuid: str,
    last_match: int,
):
    con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO players (discord_account, discord_id, league_account, league_puuid, last_match) VALUES (:discord_account, :discord_id, :league_account, :league_puuid, :last_match)",
        {
            "discord_account": str(discord_account),
            "discord_id": str(discord_id),
            "league_account": str(league_account),
            "league_puuid": str(league_puuid),
            "last_match": last_match,
        },
    )
    con.commit()
    con.close()
    return f"Player Account: {league_account} Enrolled"


def get_enrolled_user(discord_account: str):
    con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM players WHERE discord_account=(:discord_account)",
        {"discord_account": str(discord_account)},
    )
    return cur.fetchall()


def get_enrolled_users():
    con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
    cur = con.cursor()
    cur.execute("SELECT * FROM players ORDER BY score DESC")
    return cur.fetchall()


def unenroll_user(discord_account: str):
    con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
    cur = con.cursor()
    cur.execute(
        "DELETE FROM players WHERE discord_account=(:discord_account)",
        {"discord_account": str(discord_account)},
    )
    con.commit()
    con.close()
    return f"{discord_account} has been unerolled"


def insert_match(
    match_id,
    player_id,
    kills,
    deaths,
    assists,
    champion,
    win,
    match_end_timestamp,
    barons,
    dragons,
    turrets,
    inhibs,
    rifts,
    pentas,
    vision_score,
):
    con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
    cur = con.cursor()
    cur.execute(
        """
                INSERT INTO matches (match_id, player_id, kills, deaths, assists, champion, win, match_end_timestamp, barons, dragons, turrets, inhibs, rifts, pentas, vision_score) VALUES(:match_id, :player_id, :kills, :deaths, :assists, :champion, :win, :match_end_timestamp, :barons, :dragons, :turrets, :inhibs, :rifts, :pentas, :vision_score)
    """,
        {
            "match_id": str(match_id),
            "player_id": str(player_id),
            "kills": int(kills),
            "deaths": deaths,
            "assists": assists,
            "champion": champion,
            "win": win,
            "match_end_timestamp": match_end_timestamp,
            "barons": barons,
            "dragons": dragons,
            "turrets": turrets,
            "inhibs": inhibs,
            "rifts": rifts,
            "pentas": pentas,
            "vision_score": vision_score,
        },
    )
    con.commit()
    con.close()
    return f"{match_id} added"


def get_matches_by_user(discord_id):
    con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
    cur = con.cursor()
    cur.execute(
        """
                SELECT kills, deaths, assists, win, barons, dragons, turrets, inhibs, rifts, pentas, vision_score FROM matches
                WHERE player_id = (:discord_id)
                ORDER BY match_end_timestamp ASC
                """,
        {"discord_id": str(discord_id)},
    )
    return cur.fetchmany(AMOUNT_OF_GAMES)


def update_last_match(discord_id, time_in_seconds):
    con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
    cur = con.cursor()
    cur.execute(
        """
                UPDATE players
                SET last_match = (:last_match)
                WHERE discord_id = (:discord_id)
                """,
        {"discord_id": str(discord_id), "last_match": time_in_seconds},
    )
    con.commit()
    con.close()


def update_complete_status_by_user(discord_id, status: int):
    con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
    cur = con.cursor()
    cur.execute(
        """
                UPDATE players
                SET complete_status = (:status)
                WHERE discord_id = (:discord_id)
                """,
        {"discord_id": str(discord_id), "status": status},
    )
    con.commit()
    con.close()


def update_score_by_user(
    discord_id,
    score: int,
    total_kills: int,
    total_deaths: int,
    total_assists: int,
    total_wins: int,
    total_barons: int,
    total_dragons: int,
    total_turrets: int,
    total_inhibs: int,
    kda_score: int,
    total_rifts: int,
    total_pentas: int,
    total_vision_score: int,
):
    con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
    cur = con.cursor()
    cur.execute(
        """
                UPDATE players
                SET score = :score,
                    total_kills = :total_kills,
                    total_deaths = :total_deaths,
                    total_deaths = :total_deaths,
                    total_assists = :total_assists,
                    total_wins = :total_wins,
                    total_barons = :total_barons,
                    total_dragons = :total_dragons,
                    total_turrets = :total_turrets,
                    total_inhibs = :total_inhibs,
                    kda_score = :kda_score,
                    total_rifts = :total_rifts,
                    total_pentas = :total_pentas,
                    total_vision_score = :total_vision_score

                WHERE discord_id = :discord_id
                """,
        {
            "discord_id": discord_id,
            "score": score,
            "total_kills": total_kills,
            "total_deaths": total_deaths,
            "total_assists": total_assists,
            "total_wins": total_wins,
            "total_barons": total_barons,
            "total_dragons": total_dragons,
            "total_turrets": total_turrets,
            "total_inhibs": total_inhibs,
            "kda_score": kda_score,
            "total_rifts": total_rifts,
            "total_pentas": total_pentas,
            "total_vision_score": total_vision_score,
        },
    )
    con.commit()
    con.close()


def update_matches_completed_by_user(discord_id):
    con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
    cur = con.cursor()
    cur.execute(
        """
                UPDATE players
                SET matches_completed = matches_completed + 1
                WHERE discord_id = :discord_id
                """,
        {"discord_id": str(discord_id)},
    )
    con.commit()
    con.close()


def clear_matches_and_players():
    con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
    cur = con.cursor()
    cur.execute(
        """
                DELETE
                FROM matches;
    """
    )
    cur.execute(
        """
                DELETE
                FROM players;
    """
    )
    con.commit()
    con.close()


def get_winner_loser():
    con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
    cur = con.cursor()
    cur.execute("SELECT * FROM winner_loser ORDER BY score DESC")
    return cur.fetchall()


def delete_winner_loser():
    con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
    cur = con.cursor()
    cur.execute(
        """
                DELETE
                FROM winner_loser;
    """
    )
    con.commit()
    con.close()


def insert_into_winner_loser(discord_account: str, discord_id: str, score: int):
    con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
    cur = con.cursor()
    if len(get_winner_loser()) > 1:
        delete_winner_loser()
    cur.execute(
        """
                INSERT INTO winner_loser(
                    discord_account,
                    discord_id,
                    score
                )
                VALUES(
                    :discord_account,
                    :discord_id,
                    :score

                );
                """,
        {
            "discord_account": discord_account,
            "discord_id": str(discord_id),
            "score": int(score),
        },
    )
    con.commit()
    con.close()
