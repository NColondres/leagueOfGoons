from os import path
import sqlite3

PLAYERS_DATABASE = 'players_data.db'

def create_database(name: str):
    if not path.isfile(f'./src/database/{name}'):
        con = sqlite3.connect(f'./src/database/{name}')
        cur = con.cursor()
        #Create Table
        cur.execute('''CREATE TABLE players
                    (discord_account text, discord_id text, league_account text, league_puuid text)''')
        con.commit()
        con.close()
        print(f'Databse "{name}" has been created')
    else:
        print(f'Databse "{name}" already exist')

create_database(PLAYERS_DATABASE)

def enroll_user(discord_account: str, discord_id: str, league_account: str, league_puuid: str):
    con = sqlite3.connect(f'./src/database/{PLAYERS_DATABASE}')
    cur = con.cursor()
    cur.execute("INSERT INTO players VALUES (:discord_account, :discord_id, :league_account, :league_puuid)", {'discord_account': str(discord_account), 'discord_id': str(discord_id), 'league_account': str(league_account), 'league_puuid': str(league_puuid)})
    con.commit()
    con.close()
    return 'Player Enrolled'

def get_enrolled_users():
    con = sqlite3.connect(f'./src/database/{PLAYERS_DATABASE}')
    cur = con.cursor()
    cur.execute("SELECT * FROM players")
    return cur.fetchall()