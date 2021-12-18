import requests
from dotenv import dotenv_values

BASEURL = dotenv_values('.env')['LEAGUE_BASE_URL']
LEAGUE_API_KEY = dotenv_values('.env')['LEAGUE_API_KEY']
HEADER = {
    "X-Riot-Token": LEAGUE_API_KEY
}

def check_league_api():
    url = f'{BASEURL}/lol/status/v4/platform-data'
    response = requests.get(url, headers= HEADER)
    if response.status_code == 200:
        return 'League API key is valid\n[Starting]\n'
    elif response.status_code == 403:
        return False
        
result = check_league_api()
if result == False:
    print('League API Key is no longer valid. Place a new League API key in ".env" file')
    quit()
else:
    print(result)

async def get_summoner_info(summoner_name: str):
    url = f'{BASEURL}/lol/summoner/v4/summoners/by-name/{summoner_name}'
    response = requests.get(url, headers=HEADER)
    if response.status_code == 404:
        return f'WOAH THERE BESSIE\n{summoner_name} not found'
    elif response.status_code == 200:
        return response.json()
    else:
        return f'Response: {response.status_code}\nSomething went wrong'

#Get League Matches using the last_match Unix epoch
def get_league_matches(league_puuid, last_match):
    url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{league_puuid}/ids?startTime={last_match}'
    response = requests.get(url, headers=HEADER)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code

def get_match_info(matchId):
    url = f'https://americas.api.riotgames.com/lol/match/v5/matches/{matchId}'
    response = requests.get(url, headers=HEADER)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code