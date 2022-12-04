import sqlite3

DUEL_DATABASE = "duel_databse.db"


def create_duel_database(name: str):
    con = sqlite3.connect(f"./src/database/{name}")
    cur = con.cursor()

    # Create tables
    cur.execute(
        """CREATE TABLE IF NOT EXISTS challenges(
                challenge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenger text,
                champion text);
                """
    )
    con.commit()
    con.close()


create_duel_database(DUEL_DATABASE)

con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
cur = con.cursor()
cur.execute(
    """
    INSERT INTO challenges (challenger, champion)
    VALUES (:challenger, :champion )
    """,
    {"challenger": "Nick_C", "champion": "Lucian"},
)

print("\nCHALLENGER DATABSE IMPORTED\n")
