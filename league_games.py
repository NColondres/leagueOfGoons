from src import database as db
import time
from datetime import datetime
from src import league
from discord_bot import bot

data = db.get_enrolled_users()

def complete_user(user: tuple):
    user_matches = db.get_matches_by_user(user[1])
    if len(user_matches) >= db.AMOUNT_OF_GAMES:
        print('Tourney Completed for:', user[0],'\n---------------------------------------\n')
        db.update_complete_status_by_user(user[1], 1)
        for match in user_matches:
            kills = match[0]
            deaths = match[1]
            assists = match[2]
            win = match[3]
            print( 'Kills:', kills, 'Deaths:', deaths, 'Assists:', assists, '**Win**' if win else '**Loss**')
            print()
        return True
    else:
        return False


if __name__ == '__main__':
    if data:
        tournament_complete_count = 0
        for user in data:
            if not user[6]:
                user_puuid = user[3]
                matches = league.get_league_matches(user_puuid, str(user[4]))
                if not matches:
                    last_match_time = datetime.fromtimestamp(user[4]).strftime('%b %d %I:%M:%S %p')
                    print(f'{user[0]} has classic no matches played since {last_match_time}\n')
                else:
                    for match in matches:
                        print(match)
                        match_info = league.get_match_info(match)
                        time.sleep(1)
                        if match_info['info']['gameMode'] == 'CLASSIC':
                            for participant in match_info['info']['participants']:
                                if participant['puuid'] == user_puuid:
                                    print('Game Ended Unix Timestamp in Seconds:', int((match_info['info']['gameEndTimestamp']) / 1000) + 10)
                                    print('Kills:', participant['kills'])
                                    print('Deaths:', participant['deaths'])
                                    print('Assists:', participant['assists'])
                                    print('Champion:', participant['championName'])
                                    print('Win:', participant['win'])
                                    db.insert_match(match, user[1], participant['kills'], participant['deaths'], participant['assists'], participant['championName'], participant['win'], int((match_info['info']['gameEndTimestamp']) / 1000))
                                    print()
                        else:
                            print('Match not a Classic game\n')
                    last_match = int((league.get_match_info(matches[0])['info']['gameEndTimestamp'] / 1000) + 10)
                    db.update_last_match(user[1], last_match)
                    time.sleep(1)
                if complete_user(user):
                    tournament_complete_count += 1

            else:
                tournament_complete_count += 1
                complete_user(user)
            

        if tournament_complete_count == len(data):
            print(f'All users have completed their {db.AMOUNT_OF_GAMES} games\n')
            for user in data:
                complete_user_matches = db.get_matches_by_user(user[1])
                score = 0
                for match in complete_user_matches:
                    kills = match[0]
                    deaths = match[1]
                    assists = match[2]
                    win = match[3]
                    if (kills + assists) / deaths >= 1:
                        if deaths > 0:
                            score += int(((kills + assists) / deaths) * 100)
                        else:
                            score += int((kills + assists) * 100)
                    if win:
                        score += 2000
                db.update_score_by_user(user[1], score)
                print(f'{user[0]} has a score of [{score}]')
                                
            
    else:
        print('Nobody is enrolled\n[Ending script]')
        quit()
    print('[End]')