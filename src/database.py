from os import path
import sqlite3
from dotenv import dotenv_values

PLAYERS_DATABASE = 'players_data.db'

def create_database(name: str):
    con = sqlite3.connect(f'./src/database/{name}')
    cur = con.cursor()
    #Create Table
    cur.execute('''CREATE TABLE IF NOT EXISTS players(
                discord_account text PRIMARY KEY,
                discord_id text UNIQUE,
                league_account text UNIQUE,
                league_puuid text UNIQUE,
                last_match INTEGER,
                complete_status INTEGER DEFAULT 0 NOT NULL);
                ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS matches(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                player_id TEXT,
                kills INTEGER,
                deaths INTEGER,
                assists INTEGER,
                champion TEXT,
                win INTEGER,
                FOREIGN KEY(player_id) REFERENCES players(discord_id)
                );''')
    con.commit()
    con.close()

create_database(PLAYERS_DATABASE)


def enroll_user(discord_account: str, discord_id: str, league_account: str, league_puuid: str, last_match: int):
    con = sqlite3.connect(f'./src/database/{PLAYERS_DATABASE}')
    cur = con.cursor()
    cur.execute("INSERT INTO players (discord_account, discord_id, league_account, league_puuid, last_match) VALUES (:discord_account, :discord_id, :league_account, :league_puuid, :last_match)", {'discord_account': str(discord_account), 'discord_id': str(discord_id), 'league_account': str(league_account), 'league_puuid': str(league_puuid), 'last_match': last_match})
    con.commit()
    con.close()
    return f'Player Account: {league_account} Enrolled'

def get_enrolled_user(discord_account: str):
    con = sqlite3.connect(f'./src/database/{PLAYERS_DATABASE}')
    cur = con.cursor()
    cur.execute("SELECT * FROM players WHERE discord_account=(:discord_account)", {'discord_account': str(discord_account)})
    return cur.fetchall()

def get_enrolled_users():
    con = sqlite3.connect(f'./src/database/{PLAYERS_DATABASE}')
    cur = con.cursor()
    cur.execute("SELECT * FROM players")
    return cur.fetchall()

def unenroll_user(discord_account: str):
    con = sqlite3.connect(f'./src/database/{PLAYERS_DATABASE}')
    cur = con.cursor()
    cur.execute("DELETE FROM players WHERE discord_account=(:discord_account)", {'discord_account': str(discord_account)})
    con.commit()
    con.close()
    return 'You have been unerolled'

def insert_match(match_id, player_id, kills, deaths, assists, champion, win):
    con = sqlite3.connect(f'./src/database/{PLAYERS_DATABASE}')
    cur = con.cursor()
    cur.execute('''
                INSERT INTO matches (match_id, player_id, kills, deaths, assists, champion, win) VALUES(:match_id, :player_id, :kills, :deaths, :assists, :champion, :win)
    ''', {'match_id': str(match_id), 'player_id': str(player_id), 'kills': int(kills), 'deaths': deaths, 'assists': assists, 'champion': champion, 'win': win})
    con.commit()
    con.close()
    return f'{match_id} added'

def update_last_match(discord_id, time_in_seconds):
    con = sqlite3.connect(f'./src/database/{PLAYERS_DATABASE}')
    cur = con.cursor()
    cur.execute('''
                UPDATE players
                SET last_match = (:last_match)
                WHERE discord_id = (:discord_id)
                ''', {
                    'discord_id': str(discord_id),
                    'last_match': time_in_seconds
                })
    con.commit()
    con.close()

def get_matches_by_user(discord_id):
    con = sqlite3.connect(f'./src/database/{PLAYERS_DATABASE}')
    cur = con.cursor()
    cur.execute('''
                SELECT kills, deaths, assists, win FROM matches
                WHERE player_id = (:discord_id)
                ORDER BY match_id ASC
                ''', {'discord_id': str(discord_id)})
    return cur.fetchmany(int(dotenv_values('.env')['NUMBER_OF_MATCHES']))