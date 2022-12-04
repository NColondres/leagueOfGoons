import sqlite3

DUEL_DATABASE = 'duel_databse.db'

def create_duel_database(name: str):
    con = sqlite3.connect(f"./src/database/{name}")
    cur = con.cursor()

    # Create tables
    