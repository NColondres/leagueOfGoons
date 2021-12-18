from src import database as db
import requests
import time
from src import league

data = db.get_enrolled_users()

if __name__ == '__main__':
    if data:
        for user in data:
            if not user[5]:
                user_puuid = user[3]
                matches = league.get_league_matches(user_puuid, str(user[4]))
                if not matches:
                    print(f'{user[0]} has no matches played since last script runtime')
                else:
                    print(matches)
                    for match in matches:
                        match_info = league.get_match_info(match)
                        time.sleep(1)
                        for participant in match_info['info']['participants']:
                            if participant['puuid'] == user_puuid:
                                print('Game Ended Timestamp in Seconds:', int((match_info['info']['gameEndTimestamp']) / 1000) + 10)
                                print('Kills:', participant['kills'])
                                print('Deaths:', participant['deaths'])
                                print('Assists:', participant['assists'])
                                print('Champion:', participant['championName'])
                                print('Win:', participant['win'])
                                db.insert_match(match, user[1], participant['kills'], participant['deaths'], participant['assists'], participant['championName'], participant['win'])
                                print()
                    last_match = int((league.get_match_info(matches[0])['info']['gameEndTimestamp'] / 1000) + 10)
                    db.update_last_match(user[1], last_match)
                    time.sleep(1)
            user_matches = db.get_matches_by_user(user[1])
            for match in user_matches:
                kills = match[0]
                deaths = match[1]
                assists = match[2]
                win = match[3]
                print( 'Kills:', kills, 'Deaths:', deaths, 'Assists:', assists, '**Win**' if win else '**Loss**')
                print()
            if len(user_matches) >= db.AMOUNT_OF_GAMES:
                print('Tourney Completed for:', user[0])
                print('Number of matches:', len(user_matches))
                db.update_complete_status_by_user(user[1], 1)
                print()
            
    else:
        print('Nobody is enrolled\n[Ending script]')
        quit()