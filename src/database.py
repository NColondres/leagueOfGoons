from os import path
import sqlite3

PLAYERS_DATABASE = 'players_data.db'

def create_database(name: str):
    con = sqlite3.connect(f'./src/database/{name}')
    cur = con.cursor()
    #Create Table
    cur.execute('''CREATE TABLE IF NOT EXISTS players
                (discord_account text PRIMARY KEY, discord_id text UNIQUE, league_account text UNIQUE, league_puuid text UNIQUE)''')
    con.commit()
    con.close()

create_database(PLAYERS_DATABASE)


def enroll_user(discord_account: str, discord_id: str, league_account: str, league_puuid: str):
    con = sqlite3.connect(f'./src/database/{PLAYERS_DATABASE}')
    cur = con.cursor()
    cur.execute("INSERT INTO players VALUES (:discord_account, :discord_id, :league_account, :league_puuid)", {'discord_account': str(discord_account), 'discord_id': str(discord_id), 'league_account': str(league_account), 'league_puuid': str(league_puuid)})
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
