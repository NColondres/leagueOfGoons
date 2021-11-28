import requests
from dotenv import dotenv_values
BASEURL = dotenv_values('.env')['LEAGUE_BASE_URL']
LEAGUE_API_KEY = dotenv_values('.env')['LEAGUE_API_KEY']

def get_summoner_info(summoner_name: str):
    url = f'{BASEURL}/lol/summoner/v4/summoners/by-name/{summoner_name}'
    response = requests.get(url, headers={"X-Riot-Token": LEAGUE_API_KEY})
    if response.status_code == 404:
        return f'You fucked up...\nPlayer not found'
    elif response.status_code == 200:
        return response.json()
    else:
        return f'Response: {response.status_code}\nSomething went wrong'
        