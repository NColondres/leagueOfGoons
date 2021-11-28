from os import path
import sqlite3


def create_database(name: str):
    if not path.isfile(f'./src/database/{name}'):
        con = sqlite3.connect(f'./src/database/{name}')
        cur = con.cursor()
        #Create Table
        cur.execute('''CREATE TABLE players
                    (discord_account text, discord_id text, league_account text, league_puuid text)''')
        con.commit()
        con.close()
    else:
        print(f'Databse "{name}" already exist')