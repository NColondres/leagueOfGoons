import sqlite3

CHALLENGE_DATABASE = "challenge_database.db"


def create_duel_database(name: str):
    con = sqlite3.connect(f"./src/database/{name}")
    cur = con.cursor()

    # Create tables
    cur.execute(
        """CREATE TABLE IF NOT EXISTS challenges(
                challenge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenger_discord_id INTEGER NOT NULL,
                acceptor_discord_id INTEGER,
                decided_champion TEXT,
                decided_role TEXT,
                challenger_match_id TEXT,
                acceptor_match_id TEXT,
                challenge_complete INTEGER DEFAULT 0);
                """
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS matches(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_id INTEGER
                match_id TEXT,
                player_id TEXT,
                kills INTEGER,
                pentaKills INTEGER,
                deaths INTEGER,
                assists INTEGER,
                champion TEXT,
                win INTEGER,
                barons INTEGER,
                dragons INTEGER,
                turrets INTEGER,
                inhibs INTEGER,
                creepScore INTEGER,
                visionScore INTEGER,
                totalHealsOnTeammates INTEGER,
                totalDamageShieldedOnTeammates INTEGER,
                totalDamageDealtToChampions INTEGER,
                match_end_timestamp INTEGER NOT NULL,
                FOREIGN KEY (challenge_id) REFERENCES challenges(challenge_id));
                """
    )
    con.commit()
    con.close()


create_duel_database(CHALLENGE_DATABASE)

async def get_challenges(challenger_discord_id: int):
    con = sqlite3.connect(f"./src/database/{PLAYERS_DATABASE}")
    cur = con.cursor()
    data = cur.execute(
        """
        Select * FROM challenges
        WHERE challenger_discord_id = (:challenger_discord_id)
        """,
        {"challenger_discord_id": str(discord_id)})
    print(data)
    print(data.description)
    print(cur.fetchall())
    
